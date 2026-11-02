<p align="center">
  <img src="../assets/readme/banners/pypi.png" alt="PyPI" width="100%">
</p>

# Arquitetura

Biblioteca Python 3.14 ou superior, com import `ai_lib` e distribuição definida pelo `pyproject.toml`. LangChain fornece a interface dos modelos, LangGraph recebe os nós de revisão e o extra `a2a` acrescenta SDK de delegação e FastAPI.

```mermaid
flowchart LR
  C[Serviço consumidor] --> L[Modelos e credenciais]
  C --> G[Revisão de entrada e saída]
  G --> L
  L -->|HTTPS e chave do provedor| P[Provedores de modelos]
  C --> J[Leitura de JWT]
  J -->|HTTP público JWKS| A[Serviço de acesso]
  C --> T[Medição de etapas]
  T --> S[Callback do consumidor]
  C --> D[Delegação opcional]
  D -->|HTTP A2A e Bearer do usuário| R[Agente remoto]
```

## Módulos

| Pasta em `src/ai_lib/` | Papel |
|---|---|
| `registry/` | Tipos de lease e erros. Nome histórico, sem registro remoto |
| `llm/` | Chat, embeddings, credenciais, falhas e preços |
| `guardrails/` | Anonimização, padrões de injeção, prompts, parsers e nós de revisão |
| `security/` | RS256 por JWKS e extração de `sub` |
| `observability/` | Callback de tokens, latência, ferramentas e custo |
| `a2a/` | Agent Card, rotas, executor e cliente opcional |

## Integrações

| Relação | Protocolo | Autenticação |
|---|---|---|
| Consumidor carrega a biblioteca | Import Python | Não se aplica |
| Chat e embeddings chamam provedores | HTTPS pelos adaptadores | Chave do ambiente |
| Identidade consulta chaves públicas | JWKS por HTTP | Assinatura RS256 e issuer esperado |
| Agente delega ao remoto | A2A por HTTP | Bearer do usuário quando fornecido |
| Medição envia etapas | Callback assíncrono | Definida pelo consumidor |

## Decisões e dados

O cliente padrão de chaves é criado uma vez por processo. Rodízio, chaves inválidas e cooldown ficam em memória protegida por lock. Não há banco próprio ou coordenação entre réplicas. Reconstruir o cliente ou reiniciar o processo permite carregar alterações do ambiente.

O `get_chat_model_with_fallback` monta uma dupla a partir dos argumentos, e o `get_chat_model_from_env` segue a ordem dos provedores que têm chave, enquanto os embeddings usam o adaptador Gemini, sem herdar a cadeia de chat.

O `decode_user_id` verifica o RS256 e o issuer e devolve `None` quando falha, reutilizando o cliente JWKS por URL, mas não verifica cargo nem participação em recurso. O `mount_a2a` usa o `InMemoryTaskStore` e não adiciona autenticação, por isso cabe ao consumidor proteger as rotas e armazenar a conversa.

## Observabilidade e versão

O `StepTracker` envia os documentos ao callback recebido, e uma falha nesse envio gera um aviso sem interromper o fluxo. O custo é estimado pela tabela local e pelos tokens reportados, e a biblioteca não tem endpoint de health próprio.

A main analisada é `a3e62c9b`, de 2026-10-30, com versão declarada `0.2.1`. As fontes são [configuração do pacote](https://github.com/Solierrr/lib-ai/blob/main/pyproject.toml), [chat](https://github.com/Solierrr/lib-ai/blob/main/src/ai_lib/llm/chat.py), [credenciais](https://github.com/Solierrr/lib-ai/blob/main/src/ai_lib/llm/env_keys.py), [JWT](https://github.com/Solierrr/lib-ai/blob/main/src/ai_lib/security/jwt.py) e [medição](https://github.com/Solierrr/lib-ai/blob/main/src/ai_lib/observability/step_tracker.py).
