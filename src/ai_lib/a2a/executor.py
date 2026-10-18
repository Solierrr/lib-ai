"""Executor A2A genérico: transforma uma função de turno em uma tarefa A2A."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Literal

from a2a.helpers.proto_helpers import new_task_from_user_message
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import Part

Persona = Literal["demandante", "profissional"]
DEFAULT_PERSONA: Persona = "demandante"


@dataclass(frozen=True)
class TurnRequest:
    """O que o serviço recebe de uma delegação."""

    text: str
    token: str | None
    persona: Persona
    conversation_id: str


@dataclass(frozen=True)
class TurnReply:
    """O que o serviço devolve. `needs_input` marca uma proposta que espera a
    decisão do usuário (aceitar, recusar ou questionar)."""

    text: str
    needs_input: bool = False


TurnHandler = Callable[[TurnRequest], Awaitable[TurnReply]]


def bearer_token(context: RequestContext) -> str | None:
    """JWT do usuário vindo de `Authorization: Bearer ...`, se houver."""
    headers = context.call_context.state.get("headers", {})
    valor = headers.get("authorization", "")
    prefixo = "bearer "
    if valor.lower().startswith(prefixo):
        return valor[len(prefixo) :].strip() or None
    return None


def persona_of(context: RequestContext) -> Persona:
    """Persona de quem pergunta, enviada em `message.metadata.persona`."""
    message = context.message
    if message is not None and "persona" in message.metadata:
        valor = message.metadata["persona"]
        if valor in ("demandante", "profissional"):
            return valor
    return DEFAULT_PERSONA


class TurnExecutor(AgentExecutor):
    """Liga uma função `TurnHandler` ao ciclo de vida de uma tarefa A2A.

    O `context_id` da tarefa vira o `conversation_id` do serviço, de modo que as
    mensagens de uma mesma delegação compartilham a memória da conversa."""

    def __init__(self, handler: TurnHandler) -> None:
        self._handler = handler

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        if context.current_task is None:
            await event_queue.enqueue_event(new_task_from_user_message(context.message))
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        request = TurnRequest(
            text=context.get_user_input(),
            token=bearer_token(context),
            persona=persona_of(context),
            conversation_id=context.context_id,
        )
        try:
            reply = await self._handler(request)
        except Exception:
            await updater.failed(
                updater.new_agent_message([Part(text="Não consegui concluir a solicitação.")])
            )
            raise
        message = updater.new_agent_message([Part(text=reply.text)])
        if reply.needs_input:
            await updater.requires_input(message)
        else:
            await updater.complete(message)

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        await updater.cancel()
