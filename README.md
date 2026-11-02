<p align="center">
  <img src="./assets/readme/banners/pypi.png" alt="PyPI" width="100%">
</p>

<p align="center">
  <img src="./assets/readme/stacks/python.png" width="100" hspace="8" alt="Python" title="Python">
  <img src="./assets/readme/stacks/pydantic.png" width="100" hspace="8" alt="Pydantic" title="Pydantic">
  <img src="./assets/readme/stacks/langchain.png" width="100" hspace="8" alt="LangChain" title="LangChain">
</p>

# Blocos compartilhados dos assistentes

[![License](https://img.shields.io/github/license/Solierrr/lib-ai)](https://github.com/Solierrr/lib-ai/blob/main/LICENSE)
[![GitHub Last Commit](https://img.shields.io/github/last-commit/Solierrr/lib-ai)](https://github.com/Solierrr/lib-ai/commits)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/Solierrr/lib-ai)](https://github.com/Solierrr/lib-ai/pulls)
[![Release](https://img.shields.io/github/v/release/Solierrr/lib-ai)](https://github.com/Solierrr/lib-ai/releases)

Esta biblioteca reúne os componentes usados pelos assistentes da plataforma para conversar, revisar solicitações e encaminhar tarefas. Ela atende às equipes que mantêm esses serviços e precisam aplicar as mesmas regras de proteção de dados, uso de provedores e medição das chamadas. Não oferece uma tela própria. Seu comportamento aparece nas respostas e nas delegações dos assistentes que a incorporam.

Os serviços Python usam LangChain e LangGraph para combinar modelos, ferramentas e etapas de revisão. A biblioteca fornece seleção de credenciais, alternativas entre provedores, leitura de JWT e comunicação entre agentes. As credenciais vêm do ambiente de cada serviço. O armazenamento das conversas e a autorização das operações continuam sob responsabilidade de quem usa os componentes.

## Aprofunde-se no Projeto!

- [OVERVIEW.md](./docs/OVERVIEW.md), capacidades e regras dos componentes.
- [ARCHITECTURE.md](./docs/ARCHITECTURE.md), módulos e integrações.
- [RUNNING.md](./docs/RUNNING.md), configuração e testes locais.
- [API.md](./docs/API.md), interface Python e delegação.
- [DEPLOY.md](./docs/DEPLOY.md), distribuição do pacote.
- [STATUS.md](./docs/STATUS.md), diferenças e limitações.
- [Fluxos](./flows/), credenciais, revisão, delegação e publicação.
- [PENDENCIAS.md](./PENDENCIAS.md), confirmações do responsável.

## Contribuindo

- [CONTRIBUTING.md](https://github.com/Solierrr/.github/blob/main/.github/CONTRIBUTING.md), convenções de contribuição.
- [CODE_OF_CONDUCT.md](https://github.com/Solierrr/.github/blob/main/CODE_OF_CONDUCT.md), código de conduta.
- [SECURITY.md](https://github.com/Solierrr/.github/blob/main/SECURITY.md), reporte de vulnerabilidade.
