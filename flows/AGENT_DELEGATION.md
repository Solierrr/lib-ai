<p align="center">
  <img src="../assets/readme/banners/pypi.png" alt="PyPI" width="100%">
</p>

# Delegação de tarefa

O cliente encaminha texto, identidade e contexto a um agente remoto.

```mermaid
sequenceDiagram
  participant C as Consumidor
  participant L as Cliente A2A
  participant R as Agente remoto
  C->>L: Texto, token e contexto
  L->>R: HTTP A2A com Bearer do usuário
  R->>R: Executar turno
  alt Precisa de decisão
    R-->>L: Requer entrada
  else Concluiu
    R-->>L: Tarefa concluída
  else Handler falhou
    R-->>L: Tarefa falhou
  end
  L-->>C: Estado, texto e identificadores
```

## Falhas e limites

Uma falha de transporte, um timeout ou uma resposta sem tarefa geram o `DelegationError`, e a proteção das rotas fica com o consumidor. O fluxo integrado está em [conversa com assistentes](https://github.com/Solierrr/docs-warehouse/blob/main/docs/flows/ASSISTANT_CHAT.md).

Fonte em [implementação](https://github.com/Solierrr/lib-ai/blob/main/src/ai_lib/a2a/executor.py).
