import httpx
import pytest
from fastapi import FastAPI

from ai_lib.a2a import (
    DelegationError,
    Skill,
    TurnExecutor,
    TurnReply,
    TurnRequest,
    build_agent_card,
    delegate,
    mount_a2a,
)

BASE = "http://agent.test"


def _app(handler) -> FastAPI:
    card = build_agent_card(
        name="Teste",
        description="Agente de teste",
        version="0.1.0",
        base_url=BASE,
        skills=[Skill(id="eco", name="Eco", description="Repete", tags=["teste"])],
    )
    app = FastAPI()
    mount_a2a(app, card, TurnExecutor(handler))
    return app


def _http(app: FastAPI, token: str | None = "jwt-do-usuario") -> httpx.AsyncClient:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), headers=headers)


async def test_agent_card_anuncia_bearer_e_habilidades():
    app = _app(lambda request: None)

    async with _http(app) as http:
        resposta = await http.get(f"{BASE}/.well-known/agent-card.json")

    card = resposta.json()
    assert card["name"] == "Teste"
    assert card["skills"][0]["id"] == "eco"
    assert "bearer" in card["securitySchemes"]
    assert card["supportedInterfaces"][0]["url"] == f"{BASE}/a2a"


async def test_delegacao_repassa_texto_token_e_persona():
    vistos: list[TurnRequest] = []

    async def handler(request: TurnRequest) -> TurnReply:
        vistos.append(request)
        return TurnReply(text=f"resposta: {request.text}")

    async with _http(_app(handler)) as http:
        resultado = await delegate(
            BASE,
            "qual placa serve?",
            token="jwt-do-usuario",
            persona="profissional",
            http_client=http,
        )

    assert resultado.outcome == "completed"
    assert resultado.text == "resposta: qual placa serve?"
    assert vistos[0].token == "jwt-do-usuario"
    assert vistos[0].persona == "profissional"
    assert vistos[0].conversation_id == resultado.context_id


async def test_persona_padrao_e_demandante():
    vistos: list[TurnRequest] = []

    async def handler(request: TurnRequest) -> TurnReply:
        vistos.append(request)
        return TurnReply(text="ok")

    async with _http(_app(handler)) as http:
        await delegate(BASE, "oi", token="t", http_client=http)

    assert vistos[0].persona == "demandante"


async def test_proposta_fica_aguardando_a_decisao_do_usuario():
    async def handler(request: TurnRequest) -> TurnReply:
        return TurnReply(text="Vou cadastrar a placa X. Aceita?", needs_input=True)

    async with _http(_app(handler)) as http:
        resultado = await delegate(BASE, "cadastra a placa X", token="t", http_client=http)

    assert resultado.outcome == "input_required"
    assert resultado.text == "Vou cadastrar a placa X. Aceita?"


async def test_mesma_conversa_reaproveita_o_context_id():
    conversas: list[str] = []

    async def handler(request: TurnRequest) -> TurnReply:
        conversas.append(request.conversation_id)
        return TurnReply(text="ok")

    async with _http(_app(handler)) as http:
        primeira = await delegate(BASE, "um", token="t", http_client=http)
        await delegate(BASE, "dois", token="t", context_id=primeira.context_id, http_client=http)

    assert conversas[0] == conversas[1]


async def test_sem_token_o_executor_recebe_none():
    vistos: list[TurnRequest] = []

    async def handler(request: TurnRequest) -> TurnReply:
        vistos.append(request)
        return TurnReply(text="ok")

    async with _http(_app(handler), token=None) as http:
        await delegate(BASE, "oi", token=None, http_client=http)

    assert vistos[0].token is None


async def test_agente_fora_do_ar_vira_delegation_error():
    def falha(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("sem conexão")

    http = httpx.AsyncClient(transport=httpx.MockTransport(falha))
    async with http:
        with pytest.raises(DelegationError):
            await delegate(BASE, "oi", token="t", http_client=http)
