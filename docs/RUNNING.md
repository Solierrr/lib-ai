<p align="center">
  <img src="../assets/readme/banners/pypi.png" alt="PyPI" width="100%">
</p>

# Execução local

São necessários o Python 3.14 ou superior, o uv, o Git, o make e um shell compatível, e no Windows os alvos do Makefile usam o Git Bash. O procedimento comum está em [execução Python](https://github.com/Solierrr/docs-warehouse/blob/main/readme/running/PYTHON.md).

## Preparar e verificar

Executar no checkout da biblioteca.

```bash
make doctor
make install
make lint
make test
make build
```

A instalação usa `uv sync --frozen --extra dev`, com o suporte A2A, e os demais alvos executam o Ruff, o pytest e o `uv build`. O `make dev` não inicia servidor, e não existe um alvo `make openapi`.

Os testes ficam em `tests/`, separados por módulo. O CI usa Python 3.14, uv 0.12.22, dependências congeladas, cobertura e build da distribuição.

## Configuração

O `make vault` lê `/service-urls` por padrão e não carrega automaticamente as chaves dos provedores no processo, por isso o consumidor disponibiliza as credenciais no ambiente.

| Nome | Uso |
|---|---|
| `GEMINI_API_KEY`, `GROQ_API_KEY`, `OPENAI_API_KEY` | Chave por provedor |
| `<PROVEDOR>_API_KEY_2` até `_9`, também sem sublinhado antes do número | Chaves adicionais |
| `<PROVEDOR>_API_KEYS` | Lista adicional separada por vírgula |
| `LLM_PROVIDER_ORDER` | Ordem para a interface que lê o ambiente |
| `LLM_MODEL_<PROVEDOR>` | Modelo, com precedência abaixo do argumento `model` |
| `LLM_TEMPERATURE_OPENAI` | Temperatura enviada pelo adaptador correspondente quando definida |

Os valores repetidos são eliminados e os marcadores de preenchimento são ignorados, e o adaptador sem modelo padrão exige configuração explícita. As credenciais nunca devem ser registradas em logs.

## Diagnóstico

O `RegistryKeysNotConfigured` indica a ausência de chave, e o `RegistryKeysUnavailable` indica chaves excluídas, inválidas ou em cooldown, sem que a seleção espere o fim do cooldown. A aplicação só tenta outro provedor quando construiu uma cadeia de fallback.

As fontes são [Makefile](https://github.com/Solierrr/lib-ai/blob/main/Makefile) e [CI](https://github.com/Solierrr/lib-ai/blob/main/.github/workflows/ci.yml).
