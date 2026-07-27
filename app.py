"""TOK/IB Çalışma Asistanı — Streamlit arayüzü.

Çalıştırmak için:
    streamlit run app.py

Buradaki en önemli teknik ayrıntı `@st.cache_resource`. Streamlit her etkileşimde
tüm script'i baştan çalıştırır; önbelleğe almasaydık her soruda modeller yeniden
yüklenirdi ve her cevap dakikalar sürerdi. Önbellekle modeller oturum boyunca
bir kez yüklenir.
"""

from __future__ import annotations

import time

import streamlit as st

import config
from src import backends, rag, store

st.set_page_config(page_title="TOK Çalışma Asistanı", page_icon="📚", layout="centered")


@st.cache_resource(show_spinner=False)
def boot():
    """Modelleri ve vektör indeksini bir kez yükler."""
    conn = store.connect(config.DB_PATH)
    info = store.stats(conn)
    embedder = backends.build_embedder(config)
    chat = backends.build_chat(config)
    assistant = rag.load_assistant(conn, config, embedder, chat)

    # Isıtma: modelin İLK çıkarımı, sonrakilerden çok daha yavaş.
    # Ölçtük — ilk soru 98 saniye, ikinci soru 8 saniye sürüyordu. Burada
    # kullanıcı beklerken zaten dönen açılış spinner'ının içinde tek kelimelik
    # bir üretim yapıp bu bedeli ödüyoruz ki gerçek ilk soru hızlı gelsin.
    try:
        for _ in chat.stream(
            [{"role": "user", "content": "merhaba"}], max_tokens=1, temperature=0.0
        ):
            break
    except Exception:  # noqa: BLE001 - ısıtma başarısızsa uygulama yine çalışsın
        pass

    return assistant, info, embedder.name, chat.name


st.title("📚 TOK Çalışma Asistanı")
st.caption(
    "IB belgelerinden cevap veren, tamamen bu bilgisayarda çalışan asistan. "
    "İnternet gerekmez, hiçbir veri dışarı çıkmaz."
)

with st.spinner("Modeller yükleniyor… (ilk açılışta biraz sürer, sonra anında açılır)"):
    try:
        assistant, info, embedding_name, chat_name = boot()
    except Exception as exc:  # noqa: BLE001
        st.error(f"Modeller yüklenemedi: {exc}")
        st.info(
            "Foundry Local sorun çıkarıyorsa yedek motorla deneyebilirsin:\n\n"
            "```bash\nRAG_BACKEND=ollama streamlit run app.py\n```"
        )
        st.stop()

if info["chunks"] == 0:
    st.warning(
        "Veritabanı boş. Önce belgeleri indekslemen gerekiyor:\n\n"
        "```bash\npython ingest.py\n```"
    )
    st.stop()

# --- Kenar çubuğu ------------------------------------------------------------

with st.sidebar:
    st.header("Ayarlar")
    top_k = st.slider(
        "Kaç belge parçası kullanılsın?",
        min_value=1,
        max_value=10,
        value=config.TOP_K,
        help=(
            "Az olursa asistan yeterli bilgi bulamayabilir. "
            "Çok olursa alakasız metin de karışır ve cevap yavaşlar."
        ),
    )

    st.divider()
    st.header("Durum")
    st.metric("İndekslenen belge", info["documents"])
    st.metric("Metin parçası", info["chunks"])
    st.caption(f"**Arama modeli:** `{embedding_name}`")
    st.caption(f"**Cevap modeli:** `{chat_name}`")
    st.caption(f"**Motor:** `{config.BACKEND}`")

    st.divider()
    if st.button("Sohbeti temizle", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption(
        "Yeni belge eklemek için dosyaları `data/documents/` içine at ve "
        "`python ingest.py` çalıştır."
    )

# --- Sohbet ------------------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

EXAMPLES = [
    "TOK sergisinde kaç nesne seçmem gerekiyor?",
    "Sergi yorumu en fazla kaç kelime olabilir?",
    "Değerlendirmede en üst seviyeyi almak için ne gerekiyor?",
]

if not st.session_state.messages:
    st.markdown("**Örnek sorular:**")
    columns = st.columns(len(EXAMPLES))
    for column, example in zip(columns, EXAMPLES):
        if column.button(example, use_container_width=True):
            st.session_state.pending = example
            st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("hits"):
            with st.expander(f"Kaynaklar ({len(message['hits'])} parça)"):
                for hit in message["hits"]:
                    st.markdown(
                        f"**{hit['filename']}** — sayfa {hit['page']} "
                        f"· benzerlik `{hit['score']:.3f}`"
                    )
                    st.caption(hit["text"])
                    st.divider()
        if message.get("elapsed"):
            st.caption(f"⏱ {message['elapsed']:.1f} saniye")

question = st.chat_input("TOK belgelerine bir şey sor…")
if not question:
    # Örnek butonlarından gelen soru
    question = st.session_state.pop("pending", None)

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        started = time.time()

        with st.spinner("Belgelerde aranıyor…"):
            hits = assistant.retrieve(question, top_k=top_k)

        answer = st.write_stream(assistant.answer_stream(question, hits))
        answer = rag.strip_thinking(answer).strip()
        elapsed = time.time() - started

        serialized = [
            {"filename": h.filename, "page": h.page, "text": h.text, "score": h.score}
            for h in hits
        ]
        if serialized:
            with st.expander(f"Kaynaklar ({len(serialized)} parça)"):
                for hit in serialized:
                    st.markdown(
                        f"**{hit['filename']}** — sayfa {hit['page']} "
                        f"· benzerlik `{hit['score']:.3f}`"
                    )
                    st.caption(hit["text"])
                    st.divider()
        st.caption(f"⏱ {elapsed:.1f} saniye")

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "hits": serialized,
            "elapsed": elapsed,
        }
    )
