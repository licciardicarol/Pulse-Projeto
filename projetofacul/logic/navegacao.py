"""Regras de redirecionamento por sessão e onboarding."""

ROTA_PERFIL = "/perfil"
ROTA_INICIO = "/inicio"
ROTA_LOGIN = "/login"

ROTAS_PRIVADAS = (
    ROTA_INICIO,
    "/treinos",
    "/refeicoes",
    "/sono",
    "/peso",
    "/relatorios",
    ROTA_PERFIL,
)

# telas de acesso que não fazem sentido para quem já está logado
ROTAS_DE_ACESSO = (ROTA_LOGIN, "/cadastro")


def normalize_route(rota: str) -> str:
    rota_limpa = "/" + rota.strip().strip("/")
    return rota_limpa.lower()


def get_home_route(onboarding_concluido: bool) -> str:
    return ROTA_INICIO if onboarding_concluido else ROTA_PERFIL


def resolve_redirect(autenticado: bool, onboarding_concluido: bool, rota: str) -> str | None:
    """Retorna a rota de destino ou None quando a página atual pode ser exibida."""
    rota_atual = normalize_route(rota)

    if rota_atual in ROTAS_DE_ACESSO:
        return get_home_route(onboarding_concluido) if autenticado else None

    if rota_atual not in ROTAS_PRIVADAS:
        return None

    if not autenticado:
        return ROTA_LOGIN

    if not onboarding_concluido and rota_atual != ROTA_PERFIL:
        return ROTA_PERFIL

    return None
