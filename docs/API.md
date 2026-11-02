<p align="center">
  <img src="../assets/readme/banners/pypi.png" alt="PyPI" width="100%">
</p>

# Interface da biblioteca

A interface é Python, e o suporte A2A monta um protocolo no servidor consumidor, sem um contrato OpenAPI próprio na distribuição.

## Chat e embeddings

`ai_lib.llm` exporta as funções de modelos. O consumidor prepara o ambiente antes da primeira seleção de credenciais.

```python
from ai_lib.llm import get_chat_model_from_env

model = get_chat_model_from_env()
response = model.invoke("Explique como organizar uma visita técnica.")
```

O `get_chat_model` escolhe um provedor, o `get_chat_model_with_fallback` monta o primário e o alternativo e o `get_chat_model_from_env` monta a sequência definida no ambiente. O modelo aceita chamadas síncronas e assíncronas, `bind_tools` e `with_structured_output`, e o `LeasedEmbeddings` fornece os vetores de consultas e documentos.

## Revisão e identidade

As fábricas `make_input_guardrail_node`, `make_output_guardrail_node` e `make_judge_node` recebem o prompt e um modelo opcional, e o estado estende o `GuardrailState`. O consumidor conecta `route` e `judge_status` ao grafo, e o bloqueio de uma entrada remove a última mensagem e inclui a resposta configurada.

`decode_user_id(token, jwks_url=..., issuer=...)` retorna o identificador ou `None`. A autorização permanece no consumidor.

## Delegação opcional

O extra `a2a` fornece `build_agent_card`, `mount_a2a`, `TurnExecutor` e `delegate`. O Agent Card fica em `/.well-known/agent-card.json` e o JSON-RPC em `/a2a`, salvo caminho personalizado.

O `delegate` recebe o texto, o token, a persona e um contexto opcional e retorna `outcome`, `text`, `task_id` e `context_id`, de modo que reutilizar o contexto continua a conversa. O timeout padrão é de 120 segundos, e o consumidor que fornece o seu próprio cliente HTTP também configura os cabeçalhos dele.

O `TurnExecutor` cria um `TurnRequest`, e uma resposta com `needs_input` pede mais entrada, enquanto a outra conclui a tarefa. Uma exceção marca a tarefa como falha e um cancelamento a marca como cancelada, sem desfazer as operações de negócio já executadas.

## Falhas

Um limite de requisições ou uma credencial inválida permitem tentar outra chave, em até três tentativas por padrão, e as demais exceções seguem para o chamador. O `DelegationError` representa um erro de comunicação ou uma resposta sem tarefa, o A2A usa os seus próprios estados e erros e o consumidor implementa o [contrato HTTP de erros](https://github.com/Solierrr/docs-warehouse/blob/main/docs/standards/ERRORS.md).

As fontes são [chat](https://github.com/Solierrr/lib-ai/blob/main/src/ai_lib/llm/chat.py), [revisão](https://github.com/Solierrr/lib-ai/blob/main/src/ai_lib/guardrails/nodes.py), [cliente A2A](https://github.com/Solierrr/lib-ai/blob/main/src/ai_lib/a2a/client.py) e [executor](https://github.com/Solierrr/lib-ai/blob/main/src/ai_lib/a2a/executor.py).
