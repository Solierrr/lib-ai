<p align="center">
  <img src="../assets/readme/banners/pypi.png" alt="PyPI" width="100%">
</p>

# Visão de produto

Os assistentes compartilham funções que aparecem em diferentes conversas. A biblioteca atende às equipes responsáveis por esses assistentes para que as regras comuns sejam mantidas em um lugar.

## Capacidades

- Tentar outra credencial quando um provedor limita uma chamada ou recusa uma chave.
- Combinar provedores alternativos quando o serviço configura essa cadeia.
- Substituir dados pessoais reconhecidos antes de avaliar uma entrada e recompor os valores na saída revisada.
- Bloquear solicitações reconhecidas como manipulação ou pedido de dados internos.
- Revisar uma resposta e solicitar nova tentativa antes de recusá-la.
- Encaminhar texto a outro agente com a identidade e o contexto informado.
- Medir duração, consumo de tokens e custo estimado.

## Regras

Falha na avaliação de entrada bloqueia o processamento. Falha na revisão de saída devolve a resposta de contingência. O juiz admite uma nova tentativa por padrão antes de bloquear uma resposta reprovada. O serviço consumidor conecta essas etapas ao seu fluxo.

A revisão não comprova um fato externo, e o consumidor escolhe as orientações, as ferramentas e as permissões. A biblioteca lê a identidade, mas não decide quem pode acessar os recursos do negócio.

As tarefas de delegação duram enquanto o processo está ativo, e a continuidade da conversa depende do armazenamento do consumidor, já que a biblioteca não tem interface visual nem cadastro próprio.