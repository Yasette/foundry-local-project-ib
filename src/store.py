"""SQLite tabanlı belge + vektör deposu.

Neden SQLite? Sunucu kurmaya gerek yok, tek dosya, Python'ın içinde hazır geliyor
ve tamamen senin diskinde duruyor — projenin "veri cihazdan çıkmaz" iddiasıyla
birebir uyumlu.

Embedding'leri JSON metni yerine float32 BLOB olarak saklıyoruz: hem ~4 kat daha
küçük yer kaplıyor hem de okurken parse etmek yerine doğrudan numpy dizisine
dönüşüyor (binlerce parçada fark ediliyor).
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    filename    TEXT NOT NULL UNIQUE,
    sha256      TEXT NOT NULL,
    n_pages     INTEGER NOT NULL,
    n_chunks    INTEGER NOT NULL,
    ingested_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chunks (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_id    INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    page      INTEGER NOT NULL,
    ordinal   INTEGER NOT NULL,
    text      TEXT NOT NULL,
    embedding BLOB NOT NULL,
    dim       INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_chunks_doc ON chunks(doc_id);

-- Hangi embedding modeliyle indekslendiğini hatırlamak için.
-- Model değişirse eski vektörler geçersizdir; karşılaştırılamazlar.
CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    # check_same_thread=False: Streamlit her etkileşimde script'i başka bir
    # iş parçacığında yeniden çalıştırıyor; bağlantı ise önbellekte duruyor.
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    return conn


# --- meta ------------------------------------------------------------------


def get_meta(conn: sqlite3.Connection, key: str) -> str | None:
    row = conn.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else None


def set_meta(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(
        "INSERT INTO meta(key, value) VALUES(?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value),
    )
    conn.commit()


# --- belgeler ---------------------------------------------------------------


def document_is_current(conn: sqlite3.Connection, filename: str, sha256: str) -> bool:
    """Bu dosya aynı içerikle zaten indekslenmiş mi? (yeniden embed'i atlamak için)"""
    row = conn.execute(
        "SELECT sha256 FROM documents WHERE filename = ?", (filename,)
    ).fetchone()
    return row is not None and row["sha256"] == sha256


def delete_document(conn: sqlite3.Connection, filename: str) -> None:
    conn.execute("DELETE FROM documents WHERE filename = ?", (filename,))
    conn.commit()


def insert_document(
    conn: sqlite3.Connection,
    filename: str,
    sha256: str,
    n_pages: int,
    chunks: list[tuple[int, str, list[float]]],
) -> int:
    """Belgeyi ve tüm parçalarını tek işlemde yazar.

    chunks: (sayfa_no, metin, embedding) üçlülerinden oluşan liste.
    """
    cur = conn.execute(
        "INSERT INTO documents(filename, sha256, n_pages, n_chunks, ingested_at) "
        "VALUES(?, ?, ?, ?, ?)",
        (
            filename,
            sha256,
            n_pages,
            len(chunks),
            datetime.now(timezone.utc).isoformat(timespec="seconds"),
        ),
    )
    doc_id = cur.lastrowid
    conn.executemany(
        "INSERT INTO chunks(doc_id, page, ordinal, text, embedding, dim) "
        "VALUES(?, ?, ?, ?, ?, ?)",
        [
            (
                doc_id,
                page,
                ordinal,
                text,
                np.asarray(vec, dtype=np.float32).tobytes(),
                len(vec),
            )
            for ordinal, (page, text, vec) in enumerate(chunks)
        ],
    )
    conn.commit()
    return doc_id


def orphan_filenames(conn: sqlite3.Connection, present: set[str]) -> list[str]:
    """Veritabanında olup klasörden silinmiş dosyalar."""
    rows = conn.execute("SELECT filename FROM documents").fetchall()
    return [r["filename"] for r in rows if r["filename"] not in present]


# --- arama için yükleme -----------------------------------------------------


def load_index(conn: sqlite3.Connection) -> tuple[np.ndarray, list[dict]]:
    """Tüm parçaları tek numpy matrisi + üstveri listesi olarak döndürür.

    Matris satırları önceden birim uzunluğa normalize edilir. Böylece kosinüs
    benzerliği tek bir matris-vektör çarpımına iner (`M @ q`) — her parça için
    ayrı döngü kurmaya gerek kalmaz.
    """
    rows = conn.execute(
        "SELECT c.id, c.page, c.text, c.embedding, c.dim, d.filename "
        "FROM chunks c JOIN documents d ON d.id = c.doc_id "
        "ORDER BY c.id"
    ).fetchall()

    if not rows:
        return np.zeros((0, 0), dtype=np.float32), []

    dim = rows[0]["dim"]
    matrix = np.zeros((len(rows), dim), dtype=np.float32)
    metadata: list[dict] = []
    for i, row in enumerate(rows):
        matrix[i] = np.frombuffer(row["embedding"], dtype=np.float32)
        metadata.append(
            {"id": row["id"], "filename": row["filename"], "page": row["page"], "text": row["text"]}
        )

    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0  # sıfır vektöre bölmeyi engelle
    matrix /= norms
    return matrix, metadata


def stats(conn: sqlite3.Connection) -> dict:
    docs = conn.execute("SELECT COUNT(*) AS n FROM documents").fetchone()["n"]
    chunks = conn.execute("SELECT COUNT(*) AS n FROM chunks").fetchone()["n"]
    return {"documents": docs, "chunks": chunks}
