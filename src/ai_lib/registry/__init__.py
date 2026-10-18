"""Tipos e erros das chaves de LLM: `KeyLease`, `Provider`, `Purpose`, `Outcome` e as exceções
`Registry*`. O nome vem da época em que as chaves eram servidas pelo google-registry; hoje elas
vêm do ambiente (`ai_lib.llm.EnvKeyClient`) e este pacote só guarda os tipos que as duas
pontas compartilharam."""

from ai_lib.registry.errors import (
    RegistryAuthError,
    RegistryError,
    RegistryKeysNotConfigured,
    RegistryKeysUnavailable,
    RegistryUnreachable,
)
from ai_lib.registry.schemas import AuthHeader, KeyLease, Outcome, Provider, Purpose

__all__ = [
    "AuthHeader",
    "KeyLease",
    "Outcome",
    "Provider",
    "Purpose",
    "RegistryAuthError",
    "RegistryError",
    "RegistryKeysNotConfigured",
    "RegistryKeysUnavailable",
    "RegistryUnreachable",
]
