import os
import threading
import time
from collections.abc import Callable, Mapping, Sequence

from ai_lib.registry import (
    KeyLease,
    Outcome,
    Provider,
    Purpose,
    RegistryKeysNotConfigured,
    RegistryKeysUnavailable,
)

PROVIDERS: tuple[Provider, ...] = ("gemini", "groq", "openai")
BASE_URLS: dict[str, str] = {
    "gemini": "https://generativelanguage.googleapis.com",
    "groq": "https://api.groq.com/openai/v1",
    "openai": "https://api.openai.com/v1",
}
DEFAULT_COOLDOWN_SECONDS = 60.0
MAX_NUMBERED_KEYS = 9


def _usable(value: str) -> bool:
    # Marcadores do Infisical ainda não preenchidos (ex.: __preencher__) não são chaves.
    return bool(value) and not value.startswith("__") and "preencher" not in value.lower()


def _read_keys(provider: str, env: Mapping[str, str]) -> list[str]:
    name = provider.upper()
    keys: list[str] = []
    # Aceita _2 e também o formato já usado no Infisical (GEMINI_API_KEY2, GROQ_API_KEY3).
    numbered = [
        variable
        for n in range(2, MAX_NUMBERED_KEYS + 1)
        for variable in (f"{name}_API_KEY_{n}", f"{name}_API_KEY{n}")
    ]
    for variable in (f"{name}_API_KEY", *numbered):
        value = (env.get(variable) or "").strip()
        if _usable(value) and value not in keys:
            keys.append(value)
    for value in (env.get(f"{name}_API_KEYS") or "").split(","):
        value = value.strip()
        if _usable(value) and value not in keys:
            keys.append(value)
    return keys


def configured_providers(env: Mapping[str, str] | None = None) -> list[Provider]:
    source = os.environ if env is None else env
    return [provider for provider in PROVIDERS if _read_keys(provider, source)]


def provider_order(env: Mapping[str, str] | None = None) -> list[Provider]:
    source = os.environ if env is None else env
    raw = (source.get("LLM_PROVIDER_ORDER") or "").strip()
    if not raw:
        return configured_providers(source)
    order = [item.strip().lower() for item in raw.split(",") if item.strip()]
    unknown = [item for item in order if item not in PROVIDERS]
    if unknown:
        raise ValueError(f"unknown providers in LLM_PROVIDER_ORDER: {', '.join(unknown)}")
    return [provider for provider in order if _read_keys(provider, source)]  # type: ignore[misc]


class EnvKeyClient:
    """Serves keys read from environment variables, with the RegistryClient interface.

    Each provider reads <PROVIDER>_API_KEY, <PROVIDER>_API_KEY_2 to _9 and the comma
    separated <PROVIDER>_API_KEYS. Keys rotate round-robin; a key that hits a rate
    limit rests for the retry-after interval (60 seconds by default) and an invalid
    key is dropped for the life of the process.
    """

    def __init__(
        self,
        env: Mapping[str, str] | None = None,
        *,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        source = os.environ if env is None else env
        self._keys: dict[str, list[str]] = {p: _read_keys(p, source) for p in PROVIDERS}
        self._clock = clock
        self._lock = threading.Lock()
        self._rest_until: dict[str, float] = {}
        self._invalid: set[str] = set()
        self._cursor: dict[str, int] = {}

    def providers(self) -> list[Provider]:
        return [provider for provider in PROVIDERS if self._keys[provider]]

    def lease(
        self,
        *,
        provider: Provider | None = None,
        purpose: Purpose | None = None,
        exclude: Sequence[str] = (),
    ) -> KeyLease:
        if provider is None:
            raise RegistryKeysNotConfigured("a provider is required for environment keys")
        keys = self._keys.get(provider, [])
        if not keys:
            raise RegistryKeysNotConfigured(f"no {provider.upper()}_API_KEY configured")
        with self._lock:
            now = self._clock()
            start = self._cursor.get(provider, 0)
            for offset in range(len(keys)):
                index = (start + offset) % len(keys)
                key_id = f"{provider}:{index}"
                if key_id in exclude or key_id in self._invalid:
                    continue
                if self._rest_until.get(key_id, 0.0) > now:
                    continue
                self._cursor[provider] = index + 1
                return KeyLease(
                    provider=provider,
                    key_id=key_id,
                    api_key=keys[index],
                    base_url=BASE_URLS[provider],
                    auth_header={"name": "Authorization", "value": f"Bearer {keys[index]}"},
                )
        raise RegistryKeysUnavailable(f"all {provider} keys are resting or invalid")

    async def alease(
        self,
        *,
        provider: Provider | None = None,
        purpose: Purpose | None = None,
        exclude: Sequence[str] = (),
    ) -> KeyLease:
        return self.lease(provider=provider, purpose=purpose, exclude=exclude)

    def report(
        self, key_id: str, outcome: Outcome, retry_after_seconds: float | None = None
    ) -> None:
        with self._lock:
            if outcome == "rate_limited":
                self._rest_until[key_id] = self._clock() + (
                    retry_after_seconds or DEFAULT_COOLDOWN_SECONDS
                )
            elif outcome == "invalid":
                self._invalid.add(key_id)

    async def areport(
        self, key_id: str, outcome: Outcome, retry_after_seconds: float | None = None
    ) -> None:
        self.report(key_id, outcome, retry_after_seconds)
