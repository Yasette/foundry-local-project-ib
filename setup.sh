#!/usr/bin/env bash
# Projeyi sıfırdan kurar. Bir kez çalıştırman yeterli.
#
#   bash setup.sh
#
set -euo pipefail

cd "$(dirname "$0")"

echo "==> Uygun Python sürümü aranıyor (3.11 / 3.12 / 3.13 gerekli)"

PYTHON=""
for candidate in python3.12 python3.13 python3.11 \
                 /opt/homebrew/opt/python@3.12/bin/python3.12 \
                 /opt/homebrew/opt/python@3.13/bin/python3.13 \
                 /opt/homebrew/opt/python@3.11/bin/python3.11; do
    if command -v "$candidate" >/dev/null 2>&1; then
        PYTHON="$candidate"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "Uygun Python bulunamadı."
    echo "macOS'ta kurmak için:  brew install python@3.12"
    echo "Diğer sistemler:       https://www.python.org/downloads/"
    exit 1
fi

echo "    Kullanılacak: $PYTHON ($($PYTHON --version))"

echo "==> Sanal ortam oluşturuluyor (.venv)"
"$PYTHON" -m venv .venv

echo "==> Paketler kuruluyor"
./.venv/bin/pip install --upgrade pip --quiet
./.venv/bin/pip install -r requirements.txt

echo "==> Kurulum doğrulanıyor"
./.venv/bin/python -c "import foundry_local_sdk, streamlit, pypdf, docx, numpy; print('    tüm paketler hazır')"

cat <<'EOF'

==================================================================
Kurulum tamam. Sıradaki adımlar:

  1) Kendi belgelerini (PDF / DOCX / TXT / MD) buraya at:
         data/documents/
     (Boş bırakırsan data/sample_documents/ içindeki örnek korpus kullanılır.)

  2) Belgeleri indeksle — ilk seferde modeller inecek, birkaç dakika sürer:
         ./.venv/bin/python ingest.py

  3) Asistanı başlat:
         ./.venv/bin/streamlit run app.py

  İsteğe bağlı — testleri çalıştır:
         ./.venv/bin/python eval.py
==================================================================
EOF
