"""Belgeleri okur, parçalara böler, vektöre çevirir ve SQLite'a yazar.

Kullanım:
    python ingest.py            # sadece değişen/yeni dosyaları işler
    python ingest.py --force    # her şeyi baştan işler

Aynı dosyayı ikinci kez embed etmiyoruz: her dosyanın sha256 özeti veritabanında
duruyor, içerik değişmediyse atlanıyor. Bu yüzden ilk çalıştırma dakikalar,
sonrakiler saniyeler sürer.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import config
from src import backends, chunker, loaders, store


def iter_documents(directory: Path):
    for path in sorted(directory.iterdir()):
        if config.is_document(path):
            yield path


def embed_in_batches(embedder, texts: list[str], batch_size: int) -> list[list[float]]:
    vectors: list[list[float]] = []
    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]
        vectors.extend(embedder.embed_documents(batch))
        done = min(start + batch_size, len(texts))
        print(f"\r    vektör: {done}/{len(texts)}", end="", flush=True)
    print()
    return vectors


def main() -> int:
    parser = argparse.ArgumentParser(description="Belgeleri indeksle")
    parser.add_argument("--force", action="store_true", help="Değişmemiş dosyaları da yeniden işle")
    args = parser.parse_args()

    documents_dir = config.active_documents_dir()
    if not documents_dir.exists():
        print(f"HATA: {documents_dir} klasörü yok.", file=sys.stderr)
        return 1

    paths = list(iter_documents(documents_dir))
    if not paths:
        print(
            f"HATA: {documents_dir} içinde desteklenen dosya yok.\n"
            f"      Desteklenen türler: {', '.join(sorted(config.SUPPORTED_EXTENSIONS))}",
            file=sys.stderr,
        )
        return 1

    print(f"Klasör : {documents_dir}")
    print(f"Dosya  : {len(paths)} adet\n")

    conn = store.connect(config.DB_PATH)

    # Embedding modeli değiştiyse eski vektörler yeni sorgularla kıyaslanamaz.
    previous_model = store.get_meta(conn, "embedding_model")
    current_model = (
        config.OLLAMA_EMBEDDING_MODEL if config.BACKEND == "ollama" else config.EMBEDDING_MODEL
    )
    if previous_model and previous_model != current_model:
        print(
            f"Embedding modeli değişmiş ({previous_model} -> {current_model}).\n"
            f"Eski vektörler geçersiz, indeks sıfırlanıyor.\n"
        )
        conn.execute("DELETE FROM documents")
        conn.commit()
        args.force = True

    # Modeli ancak gerçekten embed edilecek bir şey olduğunda yüklüyoruz.
    # Hiçbir dosya değişmediyse bu adım tamamen atlanır ve ingest saniyeler
    # yerine anında biter.
    _embedder: list = []

    def embedder():
        if not _embedder:
            _embedder.append(backends.build_embedder(config))
            store.set_meta(conn, "embedding_model", _embedder[0].name)
        return _embedder[0]

    total_chunks = 0
    skipped = 0
    problems: list[str] = []
    started = time.time()

    for path in paths:
        name = path.name
        digest = loaders.file_hash(path)

        if not args.force and store.document_is_current(conn, name, digest):
            print(f"  = {name}  (değişmemiş, atlandı)")
            skipped += 1
            continue

        print(f"  + {name}")
        pages = loaders.load_document(path)

        if not pages:
            problems.append(f"{name}: hiç metin çıkarılamadı")
            print("    ! metin çıkarılamadı, atlanıyor")
            continue
        if loaders.looks_like_scan(pages):
            problems.append(f"{name}: taranmış görüntü gibi görünüyor (metin katmanı yok)")
            print("    ! taranmış PDF olabilir, atlanıyor")
            continue

        chunks = chunker.chunk_pages(
            pages,
            chunk_size=config.CHUNK_SIZE,
            overlap=config.CHUNK_OVERLAP,
            min_chars=config.MIN_CHUNK_CHARS,
        )
        if not chunks:
            problems.append(f"{name}: anlamlı parça üretilemedi")
            print("    ! anlamlı parça yok, atlanıyor")
            continue

        print(f"    {len(pages)} sayfa -> {len(chunks)} parça")
        vectors = embed_in_batches(
            embedder(), [c.text for c in chunks], config.EMBED_BATCH_SIZE
        )

        store.delete_document(conn, name)  # eski sürümü temizle
        store.insert_document(
            conn,
            filename=name,
            sha256=digest,
            n_pages=len(pages),
            chunks=[(c.page, c.text, v) for c, v in zip(chunks, vectors)],
        )
        total_chunks += len(chunks)

    # Klasörden silinmiş dosyaların indeksini de temizle
    present = {p.name for p in paths}
    for orphan in store.orphan_filenames(conn, present):
        print(f"  - {orphan}  (klasörde yok, indeksten silindi)")
        store.delete_document(conn, orphan)

    info = store.stats(conn)
    elapsed = time.time() - started

    print(f"\n{'=' * 52}")
    print(f"Bu çalıştırmada işlenen : {total_chunks} yeni parça")
    print(f"Atlanan (değişmemiş)    : {skipped} dosya")
    print(f"Toplam indeks           : {info['documents']} belge / {info['chunks']} parça")
    print(f"Süre                    : {elapsed:.1f} sn")
    print(f"Veritabanı              : {config.DB_PATH}")

    if problems:
        print(f"\nDikkat edilmesi gerekenler:")
        for problem in problems:
            print(f"  ! {problem}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
