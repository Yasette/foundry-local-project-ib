"""Model motorları: Foundry Local (ana yol) ve Ollama (yedek).

Neden iki motor var? Uygulamanın geri kalanı model çağrısını doğrudan yapsaydı,
Foundry Local'de bir sorun çıktığında (kurulum, platform, sürüm) tüm projeyi
yeniden yazmak gerekirdi. Burada ortak bir arayüz tanımlıyoruz:

    embedder.embed_documents([...])  -> list[list[float]]
    embedder.embed_query("soru")     -> list[float]
    chat.stream(messages)            -> parça parça metin üreten generator

`config.BACKEND` hangi implementasyonun kullanılacağını seçer. Uygulama kodu
hangisi olduğunu bilmez ve umursamaz.
"""

from __future__ import annotations

import json
import sys
import urllib.request
from typing import Iterator, Protocol


# --- Ortak arayüz -----------------------------------------------------------


class Embedder(Protocol):
    name: str

    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...
    def embed_query(self, text: str) -> list[float]: ...


class Chat(Protocol):
    name: str

    def stream(self, messages: list[dict], max_tokens: int, temperature: float) -> Iterator[str]: ...


# --- Foundry Local ----------------------------------------------------------

_manager = None


def _get_manager(app_name: str = "tok_rag"):
    """Foundry Local yöneticisini bir kez başlatır (singleton).

    İlk çağrıda 'execution provider' paketlerini indirir — bunlar modelin
    donanımını nasıl kullanacağını belirleyen çalışma zamanı bileşenleri.
    Apple Silicon'da bu adım genelde anında biter.
    """
    global _manager
    if _manager is not None:
        return _manager

    from foundry_local_sdk import Configuration, FoundryLocalManager

    FoundryLocalManager.initialize(Configuration(app_name=app_name))
    manager = FoundryLocalManager.instance

    try:
        manager.download_and_register_eps(
            progress_callback=lambda ep, pct: print(
                f"\r  {ep:<28} {pct:5.1f}%", end="", flush=True
            )
        )
        print(file=sys.stderr)
    except Exception as exc:  # noqa: BLE001 - EP indirimi zorunlu değil
        print(f"  (execution provider adımı atlandı: {exc})", file=sys.stderr)

    _manager = manager
    return manager


def list_catalog_aliases() -> list[str]:
    """Katalogdaki model takma adlarını döndürür (hangisi var, hangisi yok)."""
    manager = _get_manager()
    catalog = manager.catalog
    for attr in ("get_models", "list_models", "models"):
        getter = getattr(catalog, attr, None)
        if getter is None:
            continue
        models = getter() if callable(getter) else getter
        aliases = []
        for m in models:
            alias = getattr(m, "alias", None) or getattr(m, "id", None)
            if alias:
                aliases.append(str(alias))
        if aliases:
            return sorted(set(aliases))
    return []


def _load_foundry_model(alias: str, label: str):
    manager = _get_manager()
    model = manager.catalog.get_model(alias)
    if model is None:
        raise RuntimeError(f"'{alias}' modeli katalogda bulunamadı.")

    printed = {"done": False}

    def progress(pct: float) -> None:
        print(f"\r  {label} indiriliyor: {pct:5.1f}%", end="", flush=True)
        if pct >= 100 and not printed["done"]:
            printed["done"] = True

    model.download(progress)
    if printed["done"]:
        print()
    model.load()
    return model


class FoundryEmbedder:
    def __init__(self, alias: str):
        self.name = alias
        self._model = _load_foundry_model(alias, f"embedding modeli ({alias})")
        self._client = self._model.get_embedding_client()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        response = self._client.generate_embeddings(texts)
        return [item.embedding for item in response.data]

    def embed_query(self, text: str) -> list[float]:
        response = self._client.generate_embedding(text)
        return response.data[0].embedding


class FoundryChat:
    def __init__(self, alias: str):
        self.name = alias
        self._model = _load_foundry_model(alias, f"sohbet modeli ({alias})")
        self._client = self._model.get_chat_client()

    def stream(self, messages: list[dict], max_tokens: int, temperature: float) -> Iterator[str]:
        # SDK sürümleri arasında parametre adları oynayabiliyor; desteklemiyorsa
        # varsayılanlarla devam et (cevap yine gelir, sadece ayar uygulanmaz).
        try:
            stream = self._client.complete_streaming_chat(
                messages, max_tokens=max_tokens, temperature=temperature
            )
        except TypeError:
            stream = self._client.complete_streaming_chat(messages)

        for chunk in stream:
            if not getattr(chunk, "choices", None):
                continue
            delta = chunk.choices[0].delta
            content = getattr(delta, "content", None)
            if content:
                yield content


def pick_chat_alias(preferences: list[str], override: str | None) -> str:
    """Katalogda gerçekten bulunan ilk tercihi seçer."""
    if override:
        return override
    available = list_catalog_aliases()
    if not available:
        return preferences[-1]  # katalog okunamadıysa en küçük/güvenli modeli dene
    lowered = {a.lower(): a for a in available}
    for pref in preferences:
        if pref.lower() in lowered:
            return lowered[pref.lower()]
        # "qwen2.5-3b" tercihi "qwen2.5-3b-instruct-generic-cpu" gibi bir kimliğe
        # karşılık gelebiliyor; ön ek eşleşmesini de kabul et.
        for alias_lower, alias in lowered.items():
            if alias_lower.startswith(pref.lower()):
                return alias
    return available[0]


# --- Ollama yedeği ----------------------------------------------------------

OLLAMA_URL = "http://localhost:11434"


def _ollama_post(path: str, payload: dict, stream: bool = False):
    request = urllib.request.Request(
        f"{OLLAMA_URL}{path}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    response = urllib.request.urlopen(request, timeout=300)
    if stream:
        return response
    return json.loads(response.read())


class OllamaEmbedder:
    def __init__(self, model: str):
        self.name = model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return _ollama_post("/api/embed", {"model": self.name, "input": texts})["embeddings"]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


class OllamaChat:
    def __init__(self, model: str):
        self.name = model

    def stream(self, messages: list[dict], max_tokens: int, temperature: float) -> Iterator[str]:
        response = _ollama_post(
            "/api/chat",
            {
                "model": self.name,
                "messages": messages,
                "stream": True,
                "options": {"temperature": temperature, "num_predict": max_tokens},
            },
            stream=True,
        )
        for line in response:
            if not line.strip():
                continue
            data = json.loads(line)
            content = data.get("message", {}).get("content")
            if content:
                yield content
            if data.get("done"):
                break


# --- Fabrika ----------------------------------------------------------------


def build_embedder(config) -> Embedder:
    if config.BACKEND == "ollama":
        return OllamaEmbedder(config.OLLAMA_EMBEDDING_MODEL)
    return FoundryEmbedder(config.EMBEDDING_MODEL)


def build_chat(config) -> Chat:
    if config.BACKEND == "ollama":
        return OllamaChat(config.OLLAMA_CHAT_MODEL)
    alias = pick_chat_alias(config.CHAT_MODEL_PREFERENCES, config.CHAT_MODEL_OVERRIDE)
    return FoundryChat(alias)
