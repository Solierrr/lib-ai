<p align="center">
  <img src="../assets/readme/banners/pypi.png" alt="PyPI" width="100%">
</p>

# Distribuição

Não há ambiente HTTP, URL de QA ou implantação no cluster. O pacote integra o ambiente dos serviços consumidores.

## Publicação declarada

O [workflow](https://github.com/Solierrr/lib-ai/blob/main/.github/workflows/publish.yml) roda em push na main e por disparo manual. Ele lê nome e versão do `pyproject.toml` e consulta o PyPI. Resposta 200 encerra sem publicar, 404 permite os próximos jobs e outra resposta falha a consulta.

A validação instala dependências congeladas, roda Ruff e pytest e executa `uv build`. O job seguinte recebe `dist/` e publica com Trusted Publishing, ambiente `pypi` e permissão `id-token: write`.

A distribuição é `solaria-network`, versão `0.2.1`, com import `ai_lib`, publicada no índice e consumida pelos agentes por faixa de versão.

O [release-please](https://github.com/Solierrr/lib-ai/blob/main/release-please-config.json) usa release simples e atualiza a versão TOML como arquivo adicional. Publicar depende da main e da ausência da versão no índice, não apenas de uma tag. O processo comum está em [publicação de pacotes](https://github.com/Solierrr/docs-warehouse/blob/main/readme/deploy/PACKAGE_RELEASE.md).

## Adoção

Publicar uma versão não altera os serviços fixados numa faixa anterior, por isso cada consumidor atualiza e valida a sua dependência.