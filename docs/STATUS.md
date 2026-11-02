<p align="center">
  <img src="../assets/readme/banners/pypi.png" alt="PyPI" width="100%">
</p>

# Situação

Levantamento da main `a3e62c9b` em 2026-10-30.

- Chat, embeddings, credenciais, revisão, JWT, medição e A2A opcional têm implementação e testes por módulo (2026-10-30).
- O nome de distribuição e o fluxo de publicação atuais diferem dos textos antigos, e a versão em uso pelos agentes é a faixa `>=0.2,<0.3` (2026-10-30).
- O Makefile lê apenas a pasta de URLs por padrão, e o consumidor fornece as chaves para as chamadas reais (2026-10-30).
- Cooldowns são locais ao processo, sem coordenação de quota entre réplicas (2026-10-30).
- Tarefas A2A não sobrevivem ao reinício. Autenticação das rotas e persistência da conversa pertencem ao consumidor (2026-10-30).
- A função de identidade não verifica permissões do negócio. Não representa autorização de recurso (2026-10-30).
- Custo usa tabela local e falha na medição não bloqueia a resposta (2026-10-30).
- Não há handlers FastAPI comuns do contrato de erro HTTP registrados pela biblioteca. Essa camada fica nos serviços consumidores (2026-10-30).
