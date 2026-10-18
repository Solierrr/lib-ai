"""Montagem das rotas A2A em um app FastAPI."""

from a2a.server.agent_execution import AgentExecutor
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import (
    add_a2a_routes_to_fastapi,
    create_agent_card_routes,
    create_jsonrpc_routes,
)
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard
from fastapi import FastAPI

RPC_PATH = "/a2a"


def mount_a2a(
    app: FastAPI,
    card: AgentCard,
    executor: AgentExecutor,
    *,
    rpc_path: str = RPC_PATH,
) -> None:
    """Expõe o Agent Card em `/.well-known/agent-card.json` e o JSON-RPC em `rpc_path`.

    As tarefas ficam em memória: valem enquanto o processo vive, o que basta para as
    delegações curtas entre agentes. A memória da conversa continua no checkpointer do
    próprio serviço."""
    handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=InMemoryTaskStore(),
        agent_card=card,
    )
    add_a2a_routes_to_fastapi(
        app,
        agent_card_routes=create_agent_card_routes(card),
        jsonrpc_routes=create_jsonrpc_routes(handler, rpc_url=rpc_path),
    )
