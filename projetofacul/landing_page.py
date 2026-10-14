"""Landing page pública do Pulse, com identidade visual premium e responsiva."""

import reflex as rx

from styles.theme import LANDING_PAGE_CSS, THEME


NAV_ITEMS = [
    ("Como funciona", "#como-funciona"),
    ("Recursos", "#recursos"),
    ("Para quem é", "#para-quem-e"),
    ("FAQ", "#faq"),
]

PERGUNTAS_FREQUENTES = (
    ("O Pulse é grátis?", "Sim. Você cria sua conta e usa todos os registros e relatórios sem custo."),
    ("Meus dados são privados?", "Sim. Cada usuário acessa somente os próprios dados: seus registros ficam salvos na sua conta e visíveis só para você."),
    (
        "Preciso pesar a comida para registrar refeições?",
        'Não. Descreva a refeição em texto — por exemplo "2 ovos, pão integral e café" — e a IA estima calorias e macros. Se souber as quantidades exatas, a estimativa fica ainda melhor.',
    ),
    ("Funciona no celular?", "Sim. O app é responsivo e feito para uso rápido no celular, direto do navegador."),
    ("O Pulse substitui orientação profissional?", "Não. As sugestões são geradas por IA como apoio e não substituem médico, nutricionista ou personal trainer."),
)


class FaqState(rx.State):
    """Controla qual resposta do FAQ está aberta."""

    faq_aberto: int = -1

    @rx.event
    def toggle_faq(self, indice: int):
        self.faq_aberto = -1 if self.faq_aberto == indice else indice


def section_container(
    conteudo: rx.Component,
    largura_maxima: str = "1200px",
    padding_vertical: str | list[str] = THEME.SPACING["section_y"],
    padding_lateral: list[str] | None = None,
    classe: str = "",
) -> rx.Component:
    """Centraliza o conteúdo dentro do fundo de largura total da seção."""
    return rx.box(
        conteudo,
        width="100%",
        max_width=largura_maxima,
        margin_x="auto",
        padding_x=padding_lateral or ["20px", "28px", "40px"],
        padding_y=padding_vertical,
        display="flex",
        flex_direction="column",
        align_items="center",
        text_align="center",
        position="relative",
        class_name=classe,
    )


def icon_square(icon_name: str, color: str = THEME.COLORS["primary"]) -> rx.Component:
    """Cria um ícone de funcionalidade com fundo azul translúcido."""
    return rx.box(
        rx.icon(tag=icon_name, size=20, color=color),
        width="52px",
        height="52px",
        display="flex",
        align_items="center",
        justify_content="center",
        border_radius="16px",
        background_color=THEME.COLORS["primary_soft"],
        border="1px solid rgba(59, 147, 255, 0.12)",
        class_name="landing-icon",
    )


def primary_button(label: str, destination: str, width: str = "auto") -> rx.Component:
    """Cria um botão com destaque visual para conversão."""
    return rx.button(
        label,
        on_click=rx.redirect(destination),
        width=width,
        height="48px",
        background_color=THEME.COLORS["primary"],
        color=THEME.COLORS["text_primary"],
        border_radius=THEME.RADIUS["sm"],
        border="1px solid transparent",
        font_weight="700",
        font_size="15px",
        padding="0 24px",
        box_shadow="0 10px 26px rgba(43, 140, 255, 0.18)",
        _hover={
            "background_color": THEME.COLORS["primary_hover"],
            "box_shadow": "0 14px 32px rgba(43, 140, 255, 0.28)",
        },
        class_name="landing-button",
    )


def secondary_button(label: str, destination: str, width: str = "auto") -> rx.Component:
    """Cria um botão secundário em superfície escura."""
    return rx.button(
        label,
        on_click=rx.redirect(destination),
        width=width,
        height="48px",
        background_color=THEME.COLORS["background"],
        color=THEME.COLORS["text_primary"],
        border_radius="10px",
        border="1px solid rgba(255, 255, 255, 0.12)",
        font_weight="600",
        font_size="15px",
        padding="0 24px",
        _hover={
            "background_color": "rgba(255, 255, 255, 0.06)",
            "border_color": "rgba(255, 255, 255, 0.2)",
        },
        class_name="landing-button-secondary",
    )


def feature_card(icon_name: str, title: str, description: str) -> rx.Component:
    """Cria um card de funcionalidade com efeito visual de hover."""
    return rx.box(
        icon_square(icon_name),
        rx.heading(title, size="5", margin_top="18px", margin_bottom="10px"),
        rx.text(description, color=THEME.COLORS["text_secondary"], line_height="1.7"),
        border="1px solid " + THEME.COLORS["border"],
        border_radius=THEME.RADIUS["lg"],
        background_color=THEME.COLORS["surface"],
        padding=THEME.SPACING["card_padding"],
        text_align="center",
        class_name="landing-feature-card landing-reveal",
    )


def audience_item(icon_name: str, label: str) -> rx.Component:
    """Cria um item para o público-alvo com checklist."""
    return rx.box(
        rx.box(
            rx.icon(tag=icon_name, size=18, color=THEME.COLORS["primary"]),
            width="32px",
            height="32px",
            display="flex",
            align_items="center",
            justify_content="center",
            border_radius="10px",
            background_color=THEME.COLORS["primary_soft"],
        ),
        rx.text(label, font_weight="600", color=THEME.COLORS["text_primary"]),
        display="flex",
        align_items="center",
        gap="12px",
        padding="18px 20px",
        border="1px solid " + THEME.COLORS["border"],
        border_radius=THEME.RADIUS["md"],
        background_color=THEME.COLORS["surface"],
        class_name="landing-audience-item landing-reveal",
    )


def faq_item(pergunta: str, resposta: str, indice: int) -> rx.Component:
    """Cria uma pergunta nativa com resposta expansível e acessível."""
    resposta_aberta = FaqState.faq_aberto == indice
    pergunta_id = f"faq-question-{indice}"
    resposta_id = f"faq-answer-{indice}"

    return rx.box(
        rx.el.button(
            rx.text(pergunta, class_name="landing-faq-question-text"),
            rx.icon(
                tag="chevron-down",
                size=18,
                color=THEME.COLORS["text_secondary"],
                class_name="landing-faq-icon",
            ),
            id=pergunta_id,
            type="button",
            aria_expanded=resposta_aberta,
            aria_controls=resposta_id,
            on_click=FaqState.toggle_faq(indice),
            class_name="landing-faq-question",
        ),
        rx.box(
            rx.box(
                rx.text(
                    resposta,
                    color=THEME.COLORS["text_secondary"],
                    font_weight="400",
                    line_height="1.75",
                    padding_bottom="20px",
                ),
                overflow="hidden",
                min_height="0",
                class_name="landing-faq-answer-inner",
            ),
            id=resposta_id,
            role="region",
            aria_labelledby=pergunta_id,
            aria_hidden=FaqState.faq_aberto != indice,
            class_name=rx.cond(
                resposta_aberta,
                "landing-faq-answer is-open",
                "landing-faq-answer",
            ),
        ),
        border_bottom="1px solid rgba(255, 255, 255, 0.08)",
        class_name="landing-faq-item",
    )


def landing_page() -> rx.Component:
    """Retorna a nova landing page pública do Pulse."""
    return rx.box(
        rx.html(
            """
            <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\" />
            <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin />
            <link href=\"https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap\" rel=\"stylesheet\" />
            <style>""" + LANDING_PAGE_CSS + """</style>
            """,
        ),
        rx.script(
            """
            document.addEventListener('DOMContentLoaded', function () {
              const nav = document.querySelector('.landing-nav');
              const updateNav = () => {
                if (!nav) return;
                nav.classList.toggle('is-scrolled', window.scrollY > 12);
              };
              updateNav();
              window.addEventListener('scroll', updateNav, { passive: true });
            });
            """
        ),
        rx.box(
            rx.container(
                rx.hstack(
                    rx.hstack(
                        rx.box(
                            rx.icon(tag="activity", size=18, color=THEME.COLORS["text_primary"]),
                            width="36px",
                            height="36px",
                            display="flex",
                            align_items="center",
                            justify_content="center",
                            background_color=THEME.COLORS["primary"],
                            border_radius="12px",
                            box_shadow="0 8px 18px rgba(43, 140, 255, 0.24)",
                        ),
                        rx.text("Pulse", font_weight="800", font_size="20px", color=THEME.COLORS["text_primary"]),
                        gap="10px",
                        align="center",
                    ),
                    rx.hstack(
                        *[
                            rx.link(
                                label,
                                href=href,
                                color=THEME.COLORS["text_secondary"],
                                font_weight="600",
                                _hover={"color": THEME.COLORS["text_primary"]},
                                class_name="landing-nav-link",
                            )
                            for label, href in NAV_ITEMS
                        ],
                        display=["none", "none", "flex"],
                        gap="32px",
                    ),
                    rx.hstack(
                        secondary_button("Entrar", "/login", "auto"),
                        primary_button("Começar grátis", "/cadastro", "auto"),
                        gap="10px",
                    ),
                    justify="between",
                    align="center",
                    width="100%",
                    min_height="72px",
                ),
                width="100%",
                padding_x=["16px", "24px", "32px"],
                padding_y="12px",
            ),
            class_name="landing-nav",
            width="100%",
        ),
        rx.box(
            section_container(
                rx.vstack(
                    rx.box(
                        "PARA QUEM TREINA E QUER RESULTADO",
                        background_color="rgba(255,255,255,0.06)",
                        border="1px solid rgba(255,255,255,0.09)",
                        border_radius=THEME.RADIUS["pill"],
                        padding="8px 16px",
                        font_size="12px",
                        font_weight="700",
                        letter_spacing="0.12em",
                        color="#C4D7F0",
                    ),
                    rx.heading(
                        "Treino, alimentação, sono e peso — monitorados com inteligência artificial.",
                        font_size="clamp(2.25rem, 6vw, 4.5rem)",
                        margin_y="18px",
                        line_height="1.1",
                        letter_spacing="-0.02em",
                        max_width="900px",
                        margin_x="auto",
                        class_name="landing-hero-title",
                    ),
                    rx.text(
                        "A IA estima calorias do treino, analisa refeições e usa o sono para sugerir a intensidade do próximo treino — tudo em um só lugar.",
                        color=THEME.COLORS["text_secondary"],
                        font_size="20px",
                        max_width="700px",
                        line_height="1.7",
                        margin_bottom="32px",
                    ),
                    rx.hstack(
                        primary_button("Criar minha conta grátis", "/cadastro", "auto"),
                        secondary_button("Já tenho conta", "/login", "auto"),
                        gap="12px",
                        margin_bottom="0",
                        class_name="landing-hero-actions",
                        wrap="wrap",
                    ),
                    rx.text(
                        "Sem cartão de crédito. Seus registros ficam salvos na sua conta e visíveis só para você.",
                        color="#7E93B2",
                        font_size="13px",
                        margin_top="16px",
                    ),
                    align="center",
                    spacing="0",
                    width="100%",
                ),
                largura_maxima="1200px",
                padding_vertical=["72px", "96px", "120px"],
                padding_lateral=["20px", "30px", "40px"],
            ),
            class_name="landing-hero",
            width="100%",
        ),
        rx.box(
            section_container(
                rx.vstack(
                    rx.box(
                        rx.text("Como funciona", color=THEME.COLORS["primary"], font_size="13px", font_weight="700", letter_spacing="0.12em", text_transform="uppercase"),
                        rx.heading("O caminho para acompanhar a sua evolução", size="7", margin_top="10px", margin_bottom="0"),
                        rx.text("Em três passos simples, você transforma registros no seu histórico de performance.", color=THEME.COLORS["text_secondary"], max_width="620px", margin_top="10px"),
                        text_align="center",
                    ),
                    rx.grid(
                        feature_card("clipboard-list", "Passo 1 — Registre", "Adicione treinos, refeições, sono e peso em poucos segundos."),
                        feature_card("brain-circuit", "Passo 2 — A IA analisa", "Receba contexto sobre sua rotina usando somente os dados disponíveis."),
                        feature_card("trending-up", "Passo 3 — Veja a evolução", "Acompanhe tendências e ajuste sua rotina com mais clareza."),
                        columns={"base": "1", "md": "2", "lg": "3"},
                        spacing="4",
                        width="100%",
                    ),
                    spacing="7",
                    width="100%",
                ),
                largura_maxima=THEME.SPACING["container"],
                padding_lateral=["20px", "28px"],
                padding_vertical=THEME.SPACING["section_y"],
                classe="landing-section",
            ),
            id="como-funciona",
            background_color="rgba(255,255,255,0.01)",
            width="100%",
        ),
        rx.box(
            section_container(
                rx.vstack(
                    rx.box(
                        rx.text("Tudo em um só app", color=THEME.COLORS["primary"], font_size="13px", font_weight="700", letter_spacing="0.12em", text_transform="uppercase"),
                        rx.heading("Perfil, treino e saúde em uma visão integrada", size="7", margin_top="10px", margin_bottom="0"),
                        rx.text("Centralize o que importa para sua rotina e vire o seu próprio histórico de evolução.", color=THEME.COLORS["text_secondary"], max_width="620px", margin_top="10px"),
                        text_align="center",
                    ),
                    rx.grid(
                        feature_card("dumbbell", "Treinos", "Registre exercícios, duração, intensidade e progresso."),
                        feature_card("utensils-crossed", "Refeições", "Controle calorias, proteínas e horários das refeições."),
                        feature_card("moon-star", "Sono", "Acompanhe períodos, duração e qualidade do descanso."),
                        feature_card("weight", "Peso e medidas", "Monitore mudanças ao longo do tempo e da rotina."),
                        feature_card("chart-column", "Relatórios", "Explore a evolução com contexto e indicadores simples."),
                        feature_card("sparkles", "Recomendação diária", "Receba sugestões acionáveis baseadas nos seus registros."),
                        feature_card("user-round", "Perfil inteligente", "Mantenha informações pessoais e objetivos organizados."),
                        columns={"base": "1", "sm": "2", "lg": "4"},
                        spacing="4",
                        width="100%",
                    ),
                    spacing="7",
                    width="100%",
                ),
                largura_maxima=THEME.SPACING["container"],
                padding_lateral=["20px", "28px"],
                padding_vertical=THEME.SPACING["section_y"],
                classe="landing-section",
            ),
            id="recursos",
            background_color="rgba(255,255,255,0.015)",
            width="100%",
        ),
        rx.box(
            section_container(
                rx.vstack(
                    rx.box(
                        rx.text("Para quem é o Pulse", color=THEME.COLORS["primary"], font_size="13px", font_weight="700", letter_spacing="0.12em", text_transform="uppercase"),
                        rx.heading("Um app para pessoas que querem entender melhor sua rotina", size="7", margin_top="10px", margin_bottom="0"),
                        text_align="center",
                    ),
                    rx.grid(
                        audience_item("check", "Quem quer organizar objetivos e evolução."),
                        audience_item("check", "Quem treina por conta própria."),
                        audience_item("check", "Quem deseja registrar hábitos sem perder contexto."),
                        audience_item("check", "Quem quer receber sugestões com base nos próprios dados."),
                        columns={"base": "1", "md": "2"},
                        spacing="4",
                        width="100%",
                    ),
                    spacing="7",
                    width="100%",
                ),
                largura_maxima=THEME.SPACING["container"],
                padding_lateral=["20px", "28px"],
                padding_vertical=THEME.SPACING["section_y"],
                classe="landing-section",
            ),
            id="para-quem-e",
            width="100%",
        ),
        rx.box(
            section_container(
                rx.vstack(
                    rx.box(
                        rx.text("Perguntas frequentes", color=THEME.COLORS["primary"], font_size="13px", font_weight="700", letter_spacing="0.12em", text_transform="uppercase"),
                        rx.heading("Tudo que você precisa saber", size="7", margin_top="10px", margin_bottom="0"),
                        text_align="center",
                    ),
                    rx.box(
                        *[
                            faq_item(pergunta, resposta, indice)
                            for indice, (pergunta, resposta) in enumerate(PERGUNTAS_FREQUENTES)
                        ],
                        width="100%",
                        max_width="800px",
                        margin_x="auto",
                        class_name="landing-faq",
                    ),
                    spacing="7",
                    width="100%",
                ),
                largura_maxima=THEME.SPACING["container"],
                padding_lateral=["20px", "28px"],
                padding_vertical=THEME.SPACING["section_y"],
                classe="landing-section landing-faq-section",
            ),
            id="faq",
            width="100%",
        ),
        rx.box(
            section_container(
                rx.hstack(
                    rx.vstack(
                        rx.heading("Comece hoje o seu histórico", size="7", color=THEME.COLORS["text_primary"], margin_bottom="12px"),
                        rx.text("Registre sua rotina e tenha uma visão clara do que está funcionando.", color="#C4D7F0", max_width="600px"),
                        spacing="0",
                        align="start",
                    ),
                    primary_button("Criar minha conta grátis", "/cadastro", "auto"),
                    justify="between",
                    align="center",
                    width="100%",
                    wrap="wrap",
                    gap="24px",
                ),
                largura_maxima=THEME.SPACING["container"],
                padding_lateral=["24px", "30px"],
                padding_vertical="32px",
                classe="landing-cta",
            ),
            background=THEME.COLORS["hero_end"],
            border_top="1px solid rgba(255,255,255,0.08)",
            background_image="linear-gradient(135deg, rgba(43,140,255,0.18), rgba(0,55,138,0.1))",
            width="100%",
        ),
        rx.box(
            rx.container(
                rx.hstack(
                    rx.text("© 2026 Pulse", color=THEME.COLORS["text_muted"], font_size="14px"),
                    rx.text("As sugestões são geradas por IA e não substituem orientação profissional.", color=THEME.COLORS["text_muted"], font_size="14px"),
                    justify="between",
                    align="center",
                    width="100%",
                    wrap="wrap",
                    gap="12px",
                ),
                max_width=THEME.SPACING["container"],
                padding_x=["20px", "28px"],
                padding_y="32px",
                class_name="landing-footer",
            ),
            border_top="1px solid " + THEME.COLORS["border"],
            background_color=THEME.COLORS["background"],
            width="100%",
        ),
        background=THEME.COLORS["background"],
        min_height="100vh",
        class_name="landing-page",
    )


