"""Agent Card dos serviços de IA: JSON-RPC 1.0 com autenticação Bearer."""

from dataclasses import dataclass, field

from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentInterface,
    AgentSkill,
    HTTPAuthSecurityScheme,
    SecurityRequirement,
    SecurityScheme,
    StringList,
)

BEARER_SCHEME = "bearer"
PROTOCOL_VERSION = "1.0"


@dataclass(frozen=True)
class Skill:
    """Uma habilidade anunciada no Agent Card."""

    id: str
    name: str
    description: str
    tags: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)


def build_agent_card(
    *,
    name: str,
    description: str,
    version: str,
    base_url: str,
    skills: list[Skill],
    rpc_path: str = "/a2a",
) -> AgentCard:
    """Monta o Agent Card. `base_url` é a URL pública do serviço, sem barra final;
    o endpoint JSON-RPC fica em `base_url + rpc_path`. Todas as chamadas exigem o JWT
    do usuário no cabeçalho `Authorization: Bearer`, repassado de agente para agente."""
    return AgentCard(
        name=name,
        description=description,
        version=version,
        supported_interfaces=[
            AgentInterface(
                url=f"{base_url.rstrip('/')}{rpc_path}",
                protocol_binding="JSONRPC",
                protocol_version=PROTOCOL_VERSION,
            )
        ],
        capabilities=AgentCapabilities(streaming=False),
        security_schemes={
            BEARER_SCHEME: SecurityScheme(
                http_auth_security_scheme=HTTPAuthSecurityScheme(
                    scheme="Bearer",
                    bearer_format="JWT",
                    description="JWT do usuário, repassado na delegação entre agentes.",
                )
            )
        },
        security_requirements=[SecurityRequirement(schemes={BEARER_SCHEME: StringList()})],
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        skills=[
            AgentSkill(
                id=skill.id,
                name=skill.name,
                description=skill.description,
                tags=skill.tags,
                examples=skill.examples,
            )
            for skill in skills
        ],
    )
