"""Projenin tek ayar dosyası.

Bir şeyi değiştirmek istediğinde başka dosyaya dokunmana gerek yok, hepsi burada.
Her ayarın yanında ne işe yaradığı yazıyor.
"""

import os
from pathlib import Path

# --- Klasörler ---------------------------------------------------------------

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"          # kendi belgelerin (git'e girmez)
SAMPLE_DOCUMENTS_DIR = DATA_DIR / "sample_documents"  # repoda paylaşılan örnek korpus
DB_PATH = DATA_DIR / "rag.db"                   # SQLite veritabanı

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}

# Klasörün kendi açıklama dosyası belge sayılmaz
IGNORED_FILENAMES = {"readme.md"}


def is_document(path: Path) -> bool:
    return (
        path.is_file()
        and path.suffix.lower() in SUPPORTED_EXTENSIONS
        and path.name.lower() not in IGNORED_FILENAMES
    )


# İçinde belge varsa senin klasörünü, yoksa örnek korpusu kullan.
# Böylece depoyu klonlayan biri hiçbir şey eklemeden de projeyi çalıştırabilir.
def active_documents_dir() -> Path:
    if DOCUMENTS_DIR.exists() and any(is_document(p) for p in DOCUMENTS_DIR.iterdir()):
        return DOCUMENTS_DIR
    return SAMPLE_DOCUMENTS_DIR

# --- Modeller ----------------------------------------------------------------

# Hangi motor kullanılsın: "foundry" (ana yol) veya "ollama" (yedek).
# Terminalden geçici olarak değiştirmek için:  RAG_BACKEND=ollama streamlit run app.py
BACKEND = os.environ.get("RAG_BACKEND", "foundry")

# Metni vektöre çeviren model. Çok dilli olması önemli:
# belgeler İngilizce ama sorular Türkçe geliyor.
EMBEDDING_MODEL = os.environ.get("RAG_EMBEDDING_MODEL", "qwen3-embedding-0.6b")

# Cevabı yazan sohbet modeli. Katalogda bulunan İLK model kullanılır.
# Sıra önemli: baştakiler daha kaliteli, sondakiler daha hızlı/küçük.
#
# DİKKAT — "düşünen" (reasoning) modellerden kaçınıyoruz. qwen3.5-4b ve
# qwen3-4b gibi modeller cevaptan önce sayfalarca "Thinking Process..." metni
# üretiyor; ölçtük, tek cevap 129 saniye sürdü. Soru-cevap için gereksiz.
CHAT_MODEL_PREFERENCES = [
    "qwen2.5-7b",      # Türkçesi en temiz — varsayılan
    "phi-4-mini",      # 3.8B, ~3 kat hızlı; Türkçede kelime tekrarına girebiliyor
    "qwen2.5-1.5b",    # hızlı yedek, kalitesi düşük
    "phi-3.5-mini",
    "qwen2.5-0.5b",    # en küçük, en hızlı
]
# Belirli bir modeli zorlamak istersen:  RAG_CHAT_MODEL=qwen2.5-0.5b
CHAT_MODEL_OVERRIDE = os.environ.get("RAG_CHAT_MODEL")

# Ollama yedeği kullanılacaksa hangi modeller çekilsin
OLLAMA_EMBEDDING_MODEL = "nomic-embed-text"
OLLAMA_CHAT_MODEL = "qwen2.5:3b"

# --- Parçalama (chunking) ----------------------------------------------------

# Belgeler bu boyutta parçalara bölünür. Çok büyük olursa alakasız metin de
# modele gider ve cevap bulanıklaşır; çok küçük olursa cümle ortasından kesilir.
CHUNK_SIZE = 900          # karakter
CHUNK_OVERLAP = 150       # ardışık parçaların örtüşme miktarı (bağlam kopmasın diye)
MIN_CHUNK_CHARS = 80      # bundan kısa parçalar (başlık, sayfa numarası) atılır

# --- Arama ve cevap ----------------------------------------------------------

TOP_K = 5                 # modele kaç parça bağlam verilecek
MIN_SCORE = 0.20          # bu benzerlik skorunun altındaki parçalar alakasız sayılır

# Belgeler İngilizce, sorular Türkçe. Arama yapmadan ÖNCE soruyu kısa bir
# İngilizce arama sorgusuna çevirmek isabeti belirgin biçimde artırıyor:
# "sergi yorumu kaç kelime" -> "exhibition commentary word limit" sorgusu
# belgedeki "maximum 950 words" ifadesine çok daha yakın düşüyor.
# Belgelerin de Türkçe olduğu bir kurulumda bunu False yapabilirsin.
TRANSLATE_QUERY = True
EMBED_BATCH_SIZE = 32     # embedding'ler kaçarlı gruplar halinde hesaplansın
# Cevabın üst sınırı. 700'de bıraktığımızda açık uçlu bir soruya verilen cevap
# 85 saniye sürüyordu — model gereksiz yere uzatıyor. 350 hem yeterli hem de
# cevap süresini üçte birine indiriyor.
MAX_TOKENS = 350
TEMPERATURE = 0.2         # düşük = daha tutarlı, uydurmaya daha az meyilli

# Model bağlamda cevabı bulamadığında tam olarak bu cümleyi kurmalı.
# eval.py bu cümleyi arayarak "uydurmadı mı?" testini yapıyor.
NO_ANSWER_PHRASE = "Bu belgelerde bulamadım"

# Not: Küçük modeller uzun kural listelerini kötü izliyor. Ölçtüğümüzde
# 1.5B'lik bir model, cevap bağlamda AÇIKÇA yazdığı halde "bulamadım" diyordu —
# reddetme kuralını fazla hevesle uyguluyordu. Bu yüzden prompt önce "cevapla"
# diyor, reddetme ikinci planda kalıyor ve somut bir örnek veriliyor.
SYSTEM_PROMPT = f"""Sen bir IB / TOK çalışma asistanısın. Aşağıdaki belge \
alıntılarını okuyup öğrencinin sorusunu cevaplayacaksın.

Kurallar:
- Bağlamdaki bilgiyi kullan ve soruyu doğrudan cevapla.
- Cevabı her zaman TÜRKÇE yaz. Alıntılar İngilizce olabilir, sen Türkçe yaz.
- Kullandığın her bilginin sonuna kaynağını [dosya adı, s.SAYFA] biçiminde ekle.
- EN FAZLA 4 cümle yaz. Giriş cümlesi kurma, doğrudan cevaba geç.
- Soru bir sayı soruyorsa (kaç kelime, kaç nesne, kaç puan), bağlamdaki sayıyı
  dikkatle ara ve aynen aktar.
- Bağlamda gerçekten hiçbir ipucu yoksa sadece şunu yaz: "{NO_ANSWER_PHRASE}."
  Ama bağlamda cevap varsa mutlaka cevapla — gereksiz yere reddetme.

Örnek:
Bağlam: "[Rehber, s.45] The commentary has a maximum of 950 words."
Soru: "Yorum kaç kelime olabilir?"
Cevap: "Yorum en fazla 950 kelime olabilir. [Rehber, s.45]"

Bağlam:
{{context}}"""
