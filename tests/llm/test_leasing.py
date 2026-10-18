import pytest

from ai_lib.llm import leasing
from ai_lib.llm.env_keys import EnvKeyClient
from ai_lib.registry import RegistryKeysNotConfigured


@pytest.fixture(autouse=True)
def clean_default_client():
    leasing.reset_default_client()
    yield
    leasing.reset_default_client()


def test_default_client_reads_the_environment_once(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "gem-key")

    first = leasing.default_client()

    assert isinstance(first, EnvKeyClient)
    assert first.providers() == ["gemini"]
    assert leasing.default_client() is first


def test_default_client_without_keys_fails_when_a_key_is_requested(monkeypatch):
    for name in ("GEMINI_API_KEY", "GROQ_API_KEY", "OPENAI_API_KEY"):
        monkeypatch.delenv(name, raising=False)

    client = leasing.default_client()

    assert client.providers() == []
    with pytest.raises(RegistryKeysNotConfigured):
        client.lease(provider="gemini")


def test_reset_drops_the_cached_client(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "gem-key")
    first = leasing.default_client()

    leasing.reset_default_client()

    assert leasing.default_client() is not first
