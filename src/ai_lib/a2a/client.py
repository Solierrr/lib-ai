"""Cliente A2A: delega uma pergunta a outro agente repassando a identidade do usuário."""

import uuid
from dataclasses import dataclass
from typing import Literal

import httpx
from a2a.client import ClientConfig, create_client
from a2a.helpers.proto_helpers import get_message_text
from a2a.types import Message, Part, Role, SendMessageRequest, TaskState
from google.protobuf.struct_pb2 import Struct

Outcome = Literal["completed", "input_required", "failed", "canceled", "rejected", "unknown"]

_OUTCOMES: dict[int, Outcome] = {
    TaskState.TASK_STATE_COMPLETED: "completed",
    TaskState.TASK_STATE_INPUT_REQUIRED: "input_required",
    TaskState.TASK_STATE_FAILED: "failed",
    TaskState.TASK_STATE_CANCELED: "canceled",
    TaskState.TASK_STATE_REJECTED: "rejected",
}


class DelegationError(RuntimeError):
    """O agente remoto não respondeu ou respondeu algo que não é uma tarefa."""


@dataclass(frozen=True)
class DelegationResult:
    outcome: Outcome
    text: str
    task_id: str
    context_id: str


async def delegate(
    base_url: str,
    text: str,
    *,
    token: str | None,
    persona: str = "demandante",
    context_id: str | None = None,
    timeout: float = 120.0,
    http_client: httpx.AsyncClient | None = None,
) -> DelegationResult:
    """Envia `text` ao agente em `base_url` e devolve o desfecho da tarefa.

    O JWT do usuário vai em `Authorization: Bearer` e a persona em `message.metadata`.
    Passe o mesmo `context_id` para continuar a mesma conversa (por exemplo, depois de
    um `input_required`). `http_client` existe para testes."""
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    own_client = http_client is None
    client_http = http_client or httpx.AsyncClient(headers=headers, timeout=timeout)
    try:
        client = await create_client(
            base_url.rstrip("/"), ClientConfig(httpx_client=client_http, streaming=False)
        )
        metadata = Struct()
        metadata.update({"persona": persona})
        message = Message(
            role=Role.ROLE_USER,
            message_id=str(uuid.uuid4()),
            context_id=context_id or "",
            parts=[Part(text=text)],
            metadata=metadata,
        )
        task = None
        async for response in client.send_message(SendMessageRequest(message=message)):
            if response.HasField("task"):
                task = response.task
        if task is None:
            raise DelegationError("O agente remoto não devolveu uma tarefa.")
    except DelegationError:
        raise
    except Exception as error:
        raise DelegationError(f"Falha ao delegar para {base_url}: {error}") from error
    finally:
        if own_client:
            await client_http.aclose()

    state = task.status.state
    resposta = get_message_text(task.status.message) if task.status.HasField("message") else ""
    return DelegationResult(
        outcome=_OUTCOMES.get(state, "unknown"),
        text=resposta,
        task_id=task.id,
        context_id=task.context_id,
    )
