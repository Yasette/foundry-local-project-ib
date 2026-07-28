"""Asistanı sistematik olarak test eder ve `eval_results.md` raporunu üretir.

Bir chatbot'un "iyi görünmesi" ile "doğru olması" farklı şeyler. Burada iki tür
soru soruyoruz:

  1. CEVAPLANABILIR — cevabı belgelerde var. Asistan doğru kaynağı getirmeli.
  2. CEVAPLANAMAZ  — cevabı belgelerde YOK. Asistan "bulamadım" demeli.

İkincisi daha önemli. Bilmediğini uyduran bir asistan, hiç cevap vermeyenden
daha tehlikelidir — çünkü yanlış olduğunu anlamazsın.

Kullanım:
    python eval.py
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import config
from src import backends, rag, store


@dataclass
class TestCase:
    question: str
    # Cevapta geçmesi beklenen anahtar kelimelerden en az biri bulunmalı.
    # Boşsa bu bir "cevaplanamaz" testidir.
    expect_any: tuple[str, ...] = ()
    # Kaynak olarak gelmesi beklenen dosya adı parçaları — biri yeterli.
    # Aynı bilgi birden fazla belgede geçebiliyor (ör. değerlendirme ölçeği hem
    # ayrı bir PDF'te hem de ana rehberin içinde var), o yüzden tek dosya
    # dayatmak haksız bir test olurdu.
    expect_source: tuple[str, ...] = ()
    answerable: bool = True
    note: str = ""


TEST_CASES = [
    # --- Belgelerden cevaplanabilir olanlar ---
    TestCase(
        question="TOK sergisinde kaç nesne seçmem gerekiyor?",
        expect_any=("üç", "3", "three"),
        expect_source=("Exhibition", "TOK Subject Guide"),
        note="Temel bilgi — sergi kuralı",
    ),
    TestCase(
        question="Sergi yorumu en fazla kaç kelime olabilir?",
        expect_any=("950",),
        note="Sayısal kural, uydurmaya çok müsait",
    ),
    TestCase(
        question="Nesnelerin gerçek dünya bağlamı neden önemli?",
        expect_any=("bağlam", "context", "gerçek", "specific"),
        note="Kavramsal soru",
    ),
    TestCase(
        question="Değerlendirmede en üst seviyeyi (9-10) almak için ne gerekiyor?",
        # Model aynı fikri farklı kelimelerle söyleyebilir; ölçüt "doğru
        # kavramlardan bahsetti mi", "benim yazdığım eş anlamlıyı kullandı mı"
        # değil. Bu yüzden liste geniş tutuldu.
        expect_any=(
            "açık", "clearly", "gerekçe", "justification", "kanıt", "evidence",
            "bağlantı", "güçlü", "detaylı", "destek", "iyi açıkla",
        ),
        expect_source=("Rubric", "TOK Subject Guide"),
        note="Değerlendirme ölçeğinden cevaplanmalı",
    ),
    TestCase(
        question="IA prompt listesinde kaç tane soru var?",
        expect_any=("35",),
        note="35 KQ listesi belgesinden",
    ),
    TestCase(
        question="TOK sergisi kaç puan üzerinden değerlendiriliyor?",
        expect_any=("10", "puan", "mark", "internal", "assess"),
        note="Değerlendirme yapısı",
    ),
    TestCase(
        question="Bilgi soruları (knowledge questions) nedir?",
        expect_any=("bilgi", "knowledge", "soru", "question"),
        note="Temel TOK kavramı",
    ),
    TestCase(
        question="TOK dersinin bilgi alanları (areas of knowledge) hangileridir?",
        expect_any=("matematik", "mathematics", "doğa", "natural", "sanat", "arts", "tarih", "history"),
        note="Müfredat yapısı",
    ),
    TestCase(
        question="Sergi için nesne seçerken nelerden kaçınmalıyım?",
        expect_any=("genel", "generic", "kaçın", "avoid", "spesifik", "specific"),
        note="Pratik tavsiye",
    ),
    # --- Belgelerde OLMAYAN sorular: 'bulamadım' demeli ---
    TestCase(
        question="Matematik HL sınavının 2026 tarihi ne zaman?",
        answerable=False,
        note="Belgelerde yok — uydurursa kalır",
    ),
    TestCase(
        question="Okul kantininde tost kaç lira?",
        answerable=False,
        note="Tamamen alakasız konu",
    ),
    TestCase(
        question="Ay'a ilk kim ayak bastı?",
        answerable=False,
        note="Modelin genel bilgisinde var ama BELGELERDE yok — asıl sınav bu",
    ),
]


# Modele "tam olarak şunu yaz" desek bile cümleyi kendi kelimeleriyle kuruyor:
# "Bağlamda bulamadım", "Bu belgede bulamadım", "Bu bilgi belgelerde yer almıyor"...
# İlk sürümde sadece birebir eşleşme aradık ve model DOĞRU davrandığı halde
# testi kaldı saydık. Otomatik değerlendirmenin en sinsi hatası bu:
# ölçtüğünü sandığın şeyi değil, kelime tercihini ölçüyor olabilirsin.
REFUSAL_PATTERNS = (
    "bulamadım",
    "bulunmuyor",
    "yer almıyor",
    "geçmiyor",
    "bilgi yok",
    "belirtilmemiş",
    "bahsedilmiyor",
    "mevcut değil",
)


def looks_like_refusal(answer: str) -> bool:
    lowered = answer.lower()
    return any(p in lowered for p in REFUSAL_PATTERNS)


def check(case: TestCase, answer: str, hits: list[rag.Hit]) -> tuple[bool, str]:
    lowered = answer.lower()
    said_unknown = looks_like_refusal(answer)

    if not case.answerable:
        if said_unknown:
            return True, "doğru şekilde 'bulamadım' dedi"
        return False, "UYDURDU — belgelerde olmayan soruya cevap verdi"

    if said_unknown:
        return False, "cevap belgelerde var ama bulamadı"

    if case.expect_any and not any(k.lower() in lowered for k in case.expect_any):
        return False, f"beklenen ifadelerden hiçbiri yok: {case.expect_any}"

    if case.expect_source:
        sources = " ".join(h.filename for h in hits).lower()
        if not any(s.lower() in sources for s in case.expect_source):
            return False, f"beklenen kaynakların hiçbiri getirilmedi: {case.expect_source}"

    return True, "geçti"


def main() -> int:
    conn = store.connect(config.DB_PATH)
    info = store.stats(conn)
    if info["chunks"] == 0:
        print("Veritabanı boş. Önce: python ingest.py")
        return 1

    print(f"İndeks: {info['documents']} belge / {info['chunks']} parça")
    print("Modeller yükleniyor…\n")

    embedder = backends.build_embedder(config)
    chat = backends.build_chat(config)
    assistant = rag.load_assistant(conn, config, embedder, chat)

    rows = []
    passed = 0
    started = time.time()

    for i, case in enumerate(TEST_CASES, start=1):
        kind = "cevaplanabilir" if case.answerable else "CEVAPLANAMAZ"
        print(f"[{i}/{len(TEST_CASES)}] ({kind}) {case.question}")

        t0 = time.time()
        answer, hits = assistant.answer(case.question)
        elapsed = time.time() - t0

        ok, reason = check(case, answer, hits)
        passed += ok
        print(f"    {'GEÇTİ' if ok else 'KALDI'} — {reason}  ({elapsed:.1f}s)")
        print(f"    {answer[:160]}{'…' if len(answer) > 160 else ''}\n")

        rows.append(
            {
                "case": case,
                "answer": answer,
                "hits": hits,
                "ok": ok,
                "reason": reason,
                "elapsed": elapsed,
            }
        )

    total_time = time.time() - started
    avg = sum(r["elapsed"] for r in rows) / len(rows)

    print("=" * 56)
    print(f"SONUÇ: {passed}/{len(TEST_CASES)} test geçti")
    print(f"Ortalama cevap süresi: {avg:.1f} sn")

    write_report(rows, passed, avg, total_time, embedder.name, chat.name, info)
    print("Rapor yazıldı: eval_results.md")
    return 0 if passed == len(TEST_CASES) else 2


def write_report(rows, passed, avg, total_time, embedding_name, chat_name, info) -> None:
    lines = [
        "# Değerlendirme Sonuçları",
        "",
        "Bu rapor `python eval.py` ile otomatik üretildi.",
        "",
        "## Özet",
        "",
        "| | |",
        "|---|---|",
        f"| Geçen test | **{passed}/{len(rows)}** |",
        f"| Ortalama cevap süresi | {avg:.1f} sn |",
        f"| Toplam süre | {total_time:.0f} sn |",
        f"| İndeks | {info['documents']} belge / {info['chunks']} parça |",
        f"| Arama modeli | `{embedding_name}` |",
        f"| Cevap modeli | `{chat_name}` |",
        f"| Motor | `{config.BACKEND}` |",
        f"| Getirilen parça sayısı (top_k) | {config.TOP_K} |",
        "",
        "## Test tablosu",
        "",
        "| # | Soru | Tür | Sonuç | Süre |",
        "|---|------|-----|-------|------|",
    ]
    for i, row in enumerate(rows, start=1):
        case = row["case"]
        kind = "cevaplanabilir" if case.answerable else "cevaplanamaz"
        mark = "geçti" if row["ok"] else "kaldı"
        lines.append(
            f"| {i} | {case.question} | {kind} | {mark} | {row['elapsed']:.1f}s |"
        )

    lines += ["", "## Cevapların tamamı", ""]
    for i, row in enumerate(rows, start=1):
        case = row["case"]
        kind = (
            "cevaplanabilir"
            if case.answerable
            else "**cevaplanamaz** (asistan bilmediğini söylemeli)"
        )
        lines += [
            f"### {i}. {case.question}",
            "",
            f"*Tür:* {kind}  ",
            f"*Not:* {case.note}  ",
            f"*Sonuç:* {'geçti' if row['ok'] else 'kaldı'} — {row['reason']}  ",
            f"*Süre:* {row['elapsed']:.1f} sn",
            "",
            "**Cevap:**",
            "",
            "> " + (row["answer"].replace("\n", "\n> ") if row["answer"] else "(boş)"),
            "",
        ]
        if row["hits"]:
            lines.append("**Getirilen kaynaklar:**")
            lines.append("")
            for hit in row["hits"]:
                lines.append(
                    f"- `{hit.filename}` s.{hit.page} — benzerlik {hit.score:.3f}"
                )
            lines.append("")
        else:
            lines += [
                "**Getirilen kaynaklar:** yok (eşik değerin üstünde parça bulunamadı)",
                "",
            ]

    with open("eval_results.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    raise SystemExit(main())
