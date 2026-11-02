<p align="center">
  <img src="../assets/readme/banners/pypi.png" alt="PyPI" width="100%">
</p>

# Revisão de mensagens

O consumidor conecta os nós ao grafo para revisar entrada e saída.

```mermaid
flowchart TD
  A[Entrada] --> B{Padrão bloqueado?}
  B -->|Sim| C[Bloquear]
  B -->|Não| D[Anonimizar e classificar]
  D -->|Falha ou recusa| C
  D -->|Aprovada| E[Fluxo do consumidor]
  E --> F[Juiz]
  F -->|Aprovado| G[Revisar saída e recompor dados]
  F -->|Reprovado com tentativa| E
  F -->|Tentativas esgotadas| H[Resposta de bloqueio]
  G -->|Falha| I[Resposta de contingência]
  G -->|Sucesso| J[Entregar resposta]
```

## Falhas e limites

Uma falha na entrada bloqueia a mensagem e uma falha do juiz conta como reprovação, mas criar os nós não executa o fluxo inteiro, porque as transições pertencem ao consumidor.

Fonte em [implementação](https://github.com/Solierrr/lib-ai/blob/main/src/ai_lib/guardrails/nodes.py).
