import pytest

from ai_lib.llm import EnvKeyClient, get_chat_model_from_env, leasing, provider_order, resolve_model
from ai_lib.registry import RegistryKeysNotConfigured, RegistryKeysUnavailable


class Clock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


def test_reads_numbered_and_comma_separated_keys_without_duplicates():
    client = EnvKeyClient(
        {
            "GEMINI_API_KEY": "a",
            "GEMINI_API_KEY_2": "b",
            "GEMINI_API_KEYS": "b, c",
            "GROQ_API_KEY": "g",
        }
    )
    ids = [client.lease(provider="gemini").api_key for _ in range(3)]
    assert ids == ["a", "b", "c"]
    assert client.providers() == ["gemini", "groq"]


def test_rotates_round_robin_and_excludes_failed_key():
    client = EnvKeyClient({"GROQ_API_KEY": "k1", "GROQ_API_KEY_2": "k2"})
    first = client.lease(provider="groq")
    second = client.lease(provider="groq", exclude=[first.key_id])
    assert {first.api_key, second.api_key} == {"k1", "k2"}


def test_rate_limited_key_rests_until_retry_after():
    clock = Clock()
    client = EnvKeyClient({"OPENAI_API_KEY": "only"}, clock=clock)
    lease = client.lease(provider="openai")
    client.report(lease.key_id, "rate_limited", 30)
    with pytest.raises(RegistryKeysUnavailable):
        client.lease(provider="openai")
    clock.now += 31
    assert client.lease(provider="openai").api_key == "only"


def test_invalid_key_is_dropped_for_good():
    client = EnvKeyClient({"OPENAI_API_KEY": "bad", "OPENAI_API_KEY_2": "good"})
    bad = client.lease(provider="openai")
    client.report(bad.key_id, "invalid")
    assert {client.lease(provider="openai").api_key for _ in range(3)} == {"good"}


def test_provider_without_key_is_not_configured():
    with pytest.raises(RegistryKeysNotConfigured):
        EnvKeyClient({}).lease(provider="openai")


def test_provider_order_follows_variable_and_skips_providers_without_keys():
    env = {"LLM_PROVIDER_ORDER": "openai,gemini,groq", "OPENAI_API_KEY": "o", "GROQ_API_KEY": "g"}
    assert provider_order(env) == ["openai", "groq"]
    assert provider_order({"GEMINI_API_KEY": "x", "OPENAI_API_KEY": "y"}) == ["gemini", "openai"]


def test_unknown_provider_in_order_is_rejected():
    with pytest.raises(ValueError):
        provider_order({"LLM_PROVIDER_ORDER": "claude"})


def test_openai_model_has_no_default_and_comes_from_the_environment(monkeypatch):
    monkeypatch.delenv("LLM_MODEL_OPENAI", raising=False)
    with pytest.raises(ValueError):
        resolve_model("openai")
    monkeypatch.setenv("LLM_MODEL_OPENAI", "model-x")
    assert resolve_model("openai") == "model-x"
    assert resolve_model("openai", "explicit") == "explicit"
    assert resolve_model("groq") == "openai/gpt-oss-120b"


def test_chain_from_env_uses_configured_providers_in_order(monkeypatch):
    for name in ("GEMINI_API_KEY", "GROQ_API_KEY", "OPENAI_API_KEY"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("LLM_PROVIDER_ORDER", "openai,groq")
    monkeypatch.setenv("OPENAI_API_KEY", "o")
    monkeypatch.setenv("GROQ_API_KEY", "g")
    monkeypatch.setenv("LLM_MODEL_OPENAI", "model-x")
    chain = get_chat_model_from_env(client=EnvKeyClient())
    assert chain.provider == "openai"
    assert [m.provider for m in chain.fallbacks] == ["groq"]


def test_chain_from_env_fails_without_any_key(monkeypatch):
    for name in ("GEMINI_API_KEY", "GROQ_API_KEY", "OPENAI_API_KEY", "LLM_PROVIDER_ORDER"):
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(ValueError):
        get_chat_model_from_env()


def test_default_client_prefers_env_when_registry_is_not_configured(monkeypatch):
    leasing.reset_default_client()
    for name in ("REGISTRY_URL", "REGISTRY_CONSUMER_TOKEN", "LLM_KEYS_SOURCE"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("GROQ_API_KEY", "g")
    assert isinstance(leasing.default_client(), EnvKeyClient)
    leasing.reset_default_client()


def test_reads_the_infisical_naming_without_underscore():
    client = EnvKeyClient({"GEMINI_API_KEY": "a", "GEMINI_API_KEY2": "b", "GEMINI_API_KEY3": "c"})
    assert [client.lease(provider="gemini").api_key for _ in range(3)] == ["a", "b", "c"]


def test_unfilled_infisical_placeholders_are_not_keys():
    client = EnvKeyClient({"OPENAI_API_KEY": "__preencher__", "GROQ_API_KEY": "g"})
    assert client.providers() == ["groq"]


def test_openai_does_not_send_the_default_temperature_of_the_caller(monkeypatch):
    from ai_lib.llm.chat import _build_openai
    from ai_lib.registry import KeyLease

    lease = KeyLease(
        provider="openai",
        key_id="openai:0",
        api_key="k",
        base_url="https://api.openai.com/v1",
        auth_header={"name": "Authorization", "value": "Bearer k"},
    )
    monkeypatch.delenv("LLM_TEMPERATURE_OPENAI", raising=False)
    assert _build_openai(lease, "gpt-6-luna", 0.7, {}).temperature is None
    monkeypatch.setenv("LLM_TEMPERATURE_OPENAI", "1")
    assert _build_openai(lease, "gpt-6-luna", 0.7, {}).temperature == 1.0
