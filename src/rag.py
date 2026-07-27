"""RAG'ın kalbi: bul → bağlama ekle → cevap üret.

Üç adım:
  1. RETRIEVE — soruyu vektöre çevir, en yakın belge parçalarını bul.
  2. AUGMENT  — bulunan parçaları sistem prompt'una bağlam olarak göm.
  3. GENERATE — modele yazdır.

Aramanın matematiği (aslında tek satır):

    benzerlik = (a · b) / (|a| · |b|)

Yani iki vektör arasındaki açının kosinüsü. 1'e yakınsa "aynı yöne bakıyorlar",
yani aynı şeyden bahsediyorlar. Uzunluk değil YÖN önemli — uzun bir paragraf ile
kısa bir cümle aynı konudaysa yine yüksek skor alır.

Tüm parça vektörlerini önceden birim uzunluğa normalize ettiğimiz için (store.py)
formül `matris @ sorgu` matris çarpımına iner: binlerce parça milisaniyelerde
taranır, tek tek döngü kurmaya gerek kalmaz.
"""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from typing import Iterator

import numpy as np


@dataclass
class Hit:
    """Soruya yakın çıkan tek bir belge parçası."""

    filename: str
    page: int
    text: str
    score: float           # nihai (hibrit) skor
    dense_score: float = 0.0   # vektör benzerliği bileşeni
    lexical_score: float = 0.0  # kelime eşleşmesi bileşeni

    @property
    def citation(self) -> str:
        return f"[{self.filename}, s.{self.page}]"


# Kelimelere ayırma: Türkçe harfleri ve sayıları koru.
# Sayılar özellikle önemli — "950 kelime", "35 prompt" gibi sorular tam olarak
# burada kazanılıyor.
_TOKEN = re.compile(r"[0-9]+|[a-zA-ZçğıöşüÇĞİÖŞÜ]{3,}")

# Hiçbir ayırt edici bilgi taşımayan, her belgede geçen kelimeler
_STOPWORDS = {
    "the", "and", "for", "that", "this", "with", "from", "are", "was", "you",
    "your", "can", "not", "but", "has", "have", "his", "her", "its", "will",
    "ile", "için", "olan", "olarak", "gibi", "daha", "çok", "bir", "bu", "şu",
    "ve", "veya", "ama", "kaç", "nedir", "ne", "nasıl", "neden", "hangi",
    "gerekiyor", "olabilir", "var", "yok", "mı", "mi", "mu", "mü",
}


def tokenize(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN.findall(text) if t.lower() not in _STOPWORDS]


class Retriever:
    """Belleğe yüklenmiş indeks üzerinde HİBRİT arama yapar.

    Neden hibrit? İki arama yönteminin farklı kör noktaları var:

    * **Yoğun (dense) arama** — embedding vektörleri. Anlamı yakalar, dili aşar
      ("üç nesne" ↔ "three objects"). Ama tam sayıları ve özel terimleri
      bulanıklaştırır: "950 kelime" sorusu, kelime sayısından hiç bahsetmeyen
      ama konu olarak yakın bir paragrafı öne çıkarabilir.
    * **Seyrek (sparse/lexical) arama** — kelime eşleşmesi. Anlamı hiç bilmez
      ama "950", "35", "TOK" gibi tam ifadeleri şaşmaz biçimde bulur.

    İkisinin skorunu ağırlıklı toplayınca her iki güçlü yan da elde kalıyor.
    Nadir kelimelere daha çok ağırlık vermek için IDF kullanıyoruz: her belgede
    geçen bir kelimenin eşleşmesi bilgi taşımaz, sadece bir parçada geçenin
    eşleşmesi çok şey söyler.
    """

    # Nihai skor = DENSE_WEIGHT * vektör + (1 - DENSE_WEIGHT) * kelime
    DENSE_WEIGHT = 0.7

    def __init__(self, matrix: np.ndarray, metadata: list[dict], embedder):
        self.matrix = matrix          # (parça_sayısı, boyut), satırları normalize
        self.metadata = metadata
        self.embedder = embedder
        self._build_lexical_index()

    def _build_lexical_index(self) -> None:
        """Her parçanın kelime kümesini ve kelimelerin IDF ağırlığını hesaplar."""
        self.chunk_tokens: list[set[str]] = [
            set(tokenize(meta["text"])) for meta in self.metadata
        ]
        n_docs = max(len(self.chunk_tokens), 1)

        document_frequency: dict[str, int] = {}
        for tokens in self.chunk_tokens:
            for token in tokens:
                document_frequency[token] = document_frequency.get(token, 0) + 1

        # IDF = log(toplam parça / o kelimeyi içeren parça sayısı)
        # Az parçada geçen kelime -> yüksek ağırlık.
        self.idf = {
            token: float(np.log(n_docs / count))
            for token, count in document_frequency.items()
        }

    @property
    def is_empty(self) -> bool:
        return len(self.metadata) == 0

    def _lexical_scores(self, query: str) -> np.ndarray:
        """Sorgudaki kelimelerin ne kadarının (IDF ağırlıklı) parçada geçtiği."""
        query_tokens = set(tokenize(query))
        if not query_tokens:
            return np.zeros(len(self.metadata), dtype=np.float32)

        # Hiç görülmemiş kelimeye de bir ağırlık ver, yoksa payda sıfır olur
        default_idf = float(np.log(max(len(self.chunk_tokens), 1)))
        weights = {t: self.idf.get(t, default_idf) for t in query_tokens}
        total = sum(weights.values()) or 1.0

        scores = np.zeros(len(self.metadata), dtype=np.float32)
        for i, tokens in enumerate(self.chunk_tokens):
            matched = sum(w for t, w in weights.items() if t in tokens)
            scores[i] = matched / total
        return scores

    def search(self, query: str, top_k: int, min_score: float) -> list[Hit]:
        if self.is_empty:
            return []

        q = np.asarray(self.embedder.embed_query(query), dtype=np.float32)
        norm = np.linalg.norm(q)
        if norm == 0:
            return []
        q /= norm

        # Tek matris çarpımı = tüm parçalarla kosinüs benzerliği aynı anda
        dense = self.matrix @ q
        lexical = self._lexical_scores(query)
        combined = self.DENSE_WEIGHT * dense + (1 - self.DENSE_WEIGHT) * lexical

        # En yüksek top_k skoru bul (tam sıralama yapmadan; büyük indekslerde hızlı)
        k = min(top_k, len(combined))
        top_idx = np.argpartition(-combined, k - 1)[:k]
        top_idx = top_idx[np.argsort(-combined[top_idx])]

        hits = []
        for i in top_idx:
            score = float(combined[i])
            if score < min_score:
                continue  # alakasız parçayı bağlama koyma, sadece kafa karıştırır
            meta = self.metadata[i]
            hits.append(
                Hit(
                    filename=meta["filename"],
                    page=meta["page"],
                    text=meta["text"],
                    score=score,
                    dense_score=float(dense[i]),
                    lexical_score=float(lexical[i]),
                )
            )
        return hits


def build_context(hits: list[Hit]) -> str:
    """Bulunan parçaları modele verilecek tek metne çevirir.

    Her parçanın başına kaynağını yazıyoruz ki model cevabında doğru dosyayı
    ve sayfayı gösterebilsin.
    """
    blocks = []
    for hit in hits:
        blocks.append(f"{hit.citation}\n{hit.text}")
    return "\n\n---\n\n".join(blocks)


def build_messages(system_prompt_template: str, context: str, question: str) -> list[dict]:
    return [
        {"role": "system", "content": system_prompt_template.format(context=context)},
        {"role": "user", "content": question},
    ]


_THINK_BLOCK = re.compile(r"<think>.*?</think>\s*", flags=re.DOTALL | re.IGNORECASE)


def strip_thinking(text: str) -> str:
    """Bazı modeller cevabın başında <think>...</think> ile 'düşünüyor'.

    Kullanıcıya bunu göstermek istemiyoruz; sadece nihai cevabı bırakıyoruz.
    """
    return _THINK_BLOCK.sub("", text).lstrip()


TRANSLATE_SYSTEM_PROMPT = (
    "You turn a student's question into a short English search query for a "
    "document search engine. Reply with ONLY the query — no explanation, no "
    "quotes, no punctuation at the end. Keep it under 12 words. Use the "
    "terminology that would appear in an official IB document."
)


class RepetitionGuard:
    """Küçük modellerin takıldığı tekrar döngüsünü yakalar ve akışı keser.

    Gözlemledik: phi-4-mini açık uçlu bir soruda aynı cümleyi durmadan
    tekrarlamaya başladı ("Nasıl cevap vereceksin? Nasıl cevap vereceksin?...")
    ve token sınırına kadar böyle devam etti — hem saçma bir cevap hem de
    boşuna bekleme.

    Basit ve ucuz bir kontrol: üretilen metnin son bölümündeki bir ifade
    üst üste birden fazla kez geçiyorsa döngüye girmiş kabul edip kesiyoruz.
    """

    WINDOW = 60        # son kaç karaktere bakılacak
    MAX_REPEATS = 3    # aynı parça bu kadar tekrar ederse dur

    def __init__(self) -> None:
        self._text = ""

    def is_looping(self, piece: str) -> bool:
        self._text += piece
        if len(self._text) < self.WINDOW * self.MAX_REPEATS:
            return False
        tail = self._text[-self.WINDOW :].strip()
        if len(tail) < 20:
            return False
        return self._text.count(tail) >= self.MAX_REPEATS


class Assistant:
    """Retriever + sohbet modelini birleştiren üst seviye arayüz."""

    def __init__(self, retriever: Retriever, chat, config):
        self.retriever = retriever
        self.chat = chat
        self.config = config
        self._translation_cache: dict[str, str] = {}

    def translate_query(self, question: str) -> str:
        """Türkçe soruyu kısa bir İngilizce arama sorgusuna çevirir.

        Belgeler İngilizce olduğu için Türkçe bir soru hem vektör hem kelime
        aramasında dezavantajlı: "sergi yorumu kaç kelime" ile "maximum 950
        words" arasında ne anlamsal ne de sözcüksel güçlü bir bağ var.

        Çeviri başarısız olursa boş string döner — arama yine orijinal soruyla
        yapılabilsin diye.
        """
        if not self.config.TRANSLATE_QUERY:
            return ""
        if question in self._translation_cache:
            return self._translation_cache[question]

        try:
            raw = "".join(
                self.chat.stream(
                    [
                        {"role": "system", "content": TRANSLATE_SYSTEM_PROMPT},
                        {"role": "user", "content": question},
                    ],
                    max_tokens=60,
                    temperature=0.0,
                )
            )
            english = strip_thinking(raw).strip().strip('"').strip()
        except Exception:  # noqa: BLE001 - çeviri başarısızsa aramayı durdurma
            english = ""

        # Model saçmalarsa (paragraf yazarsa, boş dönerse) ilk satırı al ve ele
        english = english.split("\n")[0].strip() if english else ""
        if len(english) > 200:
            english = ""

        self._translation_cache[question] = english
        return english

    def retrieve(self, question: str, top_k: int | None = None) -> list[Hit]:
        """Hem orijinal hem çevrilmiş sorguyla arar ve sonuçları BİRLEŞTİRİR.

        Neden birleştirme? Ölçtük: çeviri bazen isabeti belirgin artırıyor
        (Türkçe soru "35 IA prompts" listesini bulamazken çevirisi buluyor),
        bazen de model saçmalayıp aramayı bozuyor ("Sergi" -> "Sergius").
        İki sonucu birleştirip her parçanın EN İYİ skorunu almak, kötü bir
        çevirinin zarar vermesini imkânsız kılıyor: çeviri ancak yeni aday
        ekleyebilir, mevcutları eleyemez.
        """
        k = top_k or self.config.TOP_K
        min_score = self.config.MIN_SCORE

        # Her iki aramadan da geniş aday havuzu topla, sonra en iyileri seç
        candidates: dict[tuple, Hit] = {}
        for query in filter(None, [question, self.translate_query(question)]):
            for hit in self.retriever.search(query, top_k=k * 2, min_score=min_score):
                key = (hit.filename, hit.page, hit.text[:80])
                existing = candidates.get(key)
                if existing is None or hit.score > existing.score:
                    candidates[key] = hit

        return sorted(candidates.values(), key=lambda h: h.score, reverse=True)[:k]

    def answer_stream(self, question: str, hits: list[Hit]) -> Iterator[str]:
        """Cevabı parça parça üretir (arayüzde akarak yazılsın diye).

        Hiç alakalı parça bulunamadıysa modeli hiç çağırmıyoruz: cevabı zaten
        bilemez, çağırmak sadece uydurma riski ve bekleme süresi demek.
        """
        if not hits:
            yield f"{self.config.NO_ANSWER_PHRASE}. Sorunu farklı kelimelerle sormayı deneyebilirsin."
            return

        messages = build_messages(
            self.config.SYSTEM_PROMPT, build_context(hits), question
        )

        guard = RepetitionGuard()
        in_think = False
        buffer = ""
        for piece in self.chat.stream(
            messages, self.config.MAX_TOKENS, self.config.TEMPERATURE
        ):
            buffer += piece
            # <think> bloklarını akış sırasında da gizle
            if not in_think and "<think>" in buffer:
                in_think = True
                buffer = buffer.split("<think>", 1)[1]
                continue
            if in_think:
                if "</think>" in buffer:
                    in_think = False
                    buffer = buffer.split("</think>", 1)[1]
                    if buffer:
                        yield buffer
                        buffer = ""
                continue
            if guard.is_looping(buffer):
                break
            yield buffer
            buffer = ""

    def answer(self, question: str, top_k: int | None = None) -> tuple[str, list[Hit]]:
        """Akış istemeyen yerler için (eval.py gibi) tek seferde tam cevap."""
        hits = self.retrieve(question, top_k)
        text = "".join(self.answer_stream(question, hits))
        return strip_thinking(text).strip(), hits


def load_assistant(conn: sqlite3.Connection, config, embedder, chat) -> Assistant:
    from . import store

    matrix, metadata = store.load_index(conn)
    return Assistant(Retriever(matrix, metadata, embedder), chat, config)
