import reflex as rx

from projetofacul.projetofacul import app, home, onboarding_page
from projetofacul.auth_page import pagina_autenticacao
from projetofacul.landing_page import FaqState, PERGUNTAS_FREQUENTES, faq_item
from styles.theme import LANDING_PAGE_CSS


def test_rota_raiz_exibe_home_publica():
    routes = {page.route: page.component for page in app.pages}

    assert routes["/"] is home
    assert routes["/cadastro"] is pagina_autenticacao
    assert routes["/login"] is pagina_autenticacao
    assert routes["/onboarding"] is onboarding_page


def test_home_possui_novas_secoes_publicas():
    component = home()
    component_text = " ".join(
        str(child)
        for child in component.children
        if hasattr(child, "children")
    )

    assert "Como funciona" in component_text
    assert "Tudo em um só app" in component_text
    assert "Para quem é o Pulse" in component_text
    assert "Perguntas frequentes" in component_text
    assert "Comece hoje o seu histórico" in component_text
    assert "Social (em breve)" not in component_text


def test_home_possui_cabecalho_ordenado():
    component = home()
    component_text = str(component)

    assert component_text.index("Pulse") < component_text.index("Entrar")
    assert component_text.index("Entrar") < component_text.index("Começar grátis")
    assert "Social (em breve)" not in component_text


def test_faq_possui_textos_e_estados_acessiveis():
    assert PERGUNTAS_FREQUENTES == (
        ("O Pulse é grátis?", "Sim. Você cria sua conta e usa todos os registros e relatórios sem custo."),
        ("Meus dados são privados?", "Sim. Cada usuário acessa somente os próprios dados: seus registros ficam salvos na sua conta e visíveis só para você."),
        (
            "Preciso pesar a comida para registrar refeições?",
            'Não. Descreva a refeição em texto — por exemplo "2 ovos, pão integral e café" — e a IA estima calorias e macros. Se souber as quantidades exatas, a estimativa fica ainda melhor.',
        ),
        ("Funciona no celular?", "Sim. O app é responsivo e feito para uso rápido no celular, direto do navegador."),
        ("O Pulse substitui orientação profissional?", "Não. As sugestões são geradas por IA como apoio e não substituem médico, nutricionista ou personal trainer."),
    )

    item = faq_item(*PERGUNTAS_FREQUENTES[0], 0)
    button, answer = item.children

    assert button.type._var_value == "button"
    assert button.id == "faq-question-0"
    assert "aria-expanded" in button.custom_attrs
    assert button.custom_attrs["aria-controls"] == "faq-answer-0"
    assert answer.id == "faq-answer-0"
    assert answer.role._var_value == "region"
    assert answer.custom_attrs["aria-labelledby"] == "faq-question-0"
    assert button.event_triggers["on_click"].events[0].handler.fn.__name__ == "toggle_faq"


def test_css_define_breakpoints_e_areas_minimais():
    assert "@media (max-width: 768px)" in LANDING_PAGE_CSS
    assert "@media (min-width: 768px)" not in LANDING_PAGE_CSS
    assert "min-height: 44px" in LANDING_PAGE_CSS
