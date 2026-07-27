"""Uzun metni, modele bağlam olarak verilebilecek küçük parçalara böler.

Neden bölüyoruz? İki sebep:
  1. Modelin bağlam penceresi sınırlı — 200 sayfalık PDF'i içine sığdıramayız.
  2. Daha önemlisi: arama hassasiyeti. Tüm belgeyi tek vektöre çevirirsen o
     vektör "belgenin ortalama anlamı" olur ve hiçbir spesifik soruya yakın
     düşmez. Küçük parçalar keskin eşleşme verir.

Parçalar birbiriyle biraz ÖRTÜŞÜR (overlap). Aksi halde tam parça sınırına denk
gelen bir cümle ikiye bölünür ve iki parçanın da anlamı bozulur.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .loaders import Page


@dataclass
class Chunk:
    page: int
    text: str


def _split_paragraphs(text: str) -> list[str]:
    """Önce paragraf, paragraf da uzunsa cümle sınırlarından böl."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    return paragraphs


def _split_long(text: str, size: int) -> list[str]:
    """Tek başına parça boyutunu aşan metni cümle sınırlarından kırpar."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    out: list[str] = []
    current = ""
    for s in sentences:
        if len(current) + len(s) + 1 <= size:
            current = f"{current} {s}".strip()
        else:
            if current:
                out.append(current)
            # Tek bir cümle bile sığmıyorsa (tablo satırı vb.) sert kes
            while len(s) > size:
                out.append(s[:size])
                s = s[size:]
            current = s
    if current:
        out.append(current)
    return out


def chunk_pages(
    pages: list[Page],
    chunk_size: int,
    overlap: int,
    min_chars: int,
) -> list[Chunk]:
    chunks: list[Chunk] = []

    for page in pages:
        buffer = ""
        for paragraph in _split_paragraphs(page.text):
            pieces = (
                _split_long(paragraph, chunk_size)
                if len(paragraph) > chunk_size
                else [paragraph]
            )
            for piece in pieces:
                if len(buffer) + len(piece) + 2 <= chunk_size:
                    buffer = f"{buffer}\n\n{piece}".strip()
                    continue
                if buffer:
                    chunks.append(Chunk(page=page.number, text=buffer))
                    # Bir sonraki parçaya öncekinin kuyruğunu taşı (örtüşme)
                    buffer = f"{buffer[-overlap:]}\n\n{piece}".strip() if overlap else piece
                else:
                    buffer = piece
        if buffer:
            chunks.append(Chunk(page=page.number, text=buffer))

    # Sayfa numarası, başlık kırıntısı gibi anlamsız kısa parçaları at
    return [c for c in chunks if len(c.text) >= min_chars and _has_words(c.text)]


def _has_words(text: str) -> bool:
    """En az birkaç gerçek kelime içeriyor mu? (sayfa numarası tablosu vb. eler)"""
    words = re.findall(r"[A-Za-zÇĞİÖŞÜçğıöşü]{3,}", text)
    return len(words) >= 8
