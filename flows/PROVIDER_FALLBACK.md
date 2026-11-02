<p align="center">
  <img src="../assets/readme/banners/pypi.png" alt="PyPI" width="100%">
</p>

# Seleção de credencial

Uma chamada escolhe uma chave elegível e pode seguir para outra chave ou provedor quando configurado.

```mermaid
flowchart TD
  A[Chamada] --> B[Selecionar chave]
  B -->|Sem chave elegível| F[Propagar falha]
  B --> C[Chamar provedor]
  C -->|Sucesso| D[Reportar e devolver resposta]
  C -->|Limite ou chave inválida| E[Cooldown ou exclusão]
  E --> G{Há tentativa restante?}
  G -->|Sim| B
  G -->|Não| F
  C -->|Outra exceção| F
  F --> H{Há modelo alternativo?}
  H -->|Sim| I[Tentar próximo modelo]
  H -->|Não| J[Encerrar com erro]
```

## Falhas e limites

Sem chave a seleção falha imediatamente, e o cooldown usa o Retry-After numérico ou 60 segundos por padrão. Uma chave inválida fica excluída durante toda a vida do cliente, e a classificação examina até cinco exceções encadeadas.

Fonte em [implementação](https://github.com/Solierrr/lib-ai/blob/main/src/ai_lib/llm/leasing.py).
