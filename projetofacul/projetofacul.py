"""Tela de cadastro do perfil do Pulse."""

import json
import os
from urllib import request

import reflex as rx

from rxconfig import config


class PerfilState(rx.State):
    """State para o cadastro inicial do perfil do usuário."""

    nome: str = ""
    data_nascimento: str = ""
    sexo: str = "Masculino"
    altura_cm: str = ""
    tipo_fisico: str = ""
    nivel_fisico: str = ""
    modalidade_fav: str = "Musculação"
    horario_fav_de_treino: str = ""
    meta_semanal: str = ""
    objetivo: str = "Hipertrofia (ganho de massa muscular)"
    medidas: bool = False
    feedback: str = ""
    feedback_tipo: str = "info"
    is_submitting: bool = False

    def set_field(self, field: str, value):
        setattr(self, field, value)
        if self.feedback:
            self.feedback = ""
            self.feedback_tipo = "info"

    def submit(self):
        if not self.nome.strip():
            self.feedback = "Informe o nome para continuar."
            self.feedback_tipo = "error"
            return

        if not self.data_nascimento:
            self.feedback = "Informe a data de nascimento."
            self.feedback_tipo = "error"
            return

        payload = {
            "nome": self.nome.strip(),
            "data_de_nascimento": self.data_nascimento,
            "sexo": self.sexo,
            "altura_cm": float(self.altura_cm) if self.altura_cm else None,
            "tipo_fisico": float(self.tipo_fisico) if self.tipo_fisico else None,
            "nivel_fisico": self.nivel_fisico.strip() if self.nivel_fisico else None,
            "modalidade_fav": self.modalidade_fav,
            "horario_fav_de_treino": int(self.horario_fav_de_treino) if self.horario_fav_de_treino else None,
            "meta_semanal": int(self.meta_semanal) if self.meta_semanal else None,
            "objetivo": self.objetivo,
            "medidas": self.medidas,
        }

        self.is_submitting = True
        base_url = os.getenv("XANO_API_URL")

        if not base_url:
            self.feedback = "Cadastro validado localmente. Configure XANO_API_URL para sincronizar com o Xano."
            self.feedback_tipo = "success"
            self.is_submitting = False
            return

        headers = {"Content-Type": "application/json"}
        api_key = os.getenv("XANO_API_KEY")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        try:
            req = request.Request(
                f"{base_url.rstrip('/')}/profiles",
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            with request.urlopen(req, timeout=20) as response:
                if response.status >= 400:
                    raise RuntimeError(f"Erro do servidor: {response.status}")
            self.feedback = "Perfil cadastrado com sucesso!"
            self.feedback_tipo = "success"
        except Exception as exc:  # pragma: no cover - tratamento de integração
            self.feedback = f"Não foi possível salvar o perfil no Xano: {exc}"
            self.feedback_tipo = "error"
        finally:
            self.is_submitting = False


def field_label(text: str) -> rx.Component:
    return rx.text(text, size="3", weight="medium", color="gray")


def index() -> rx.Component:
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.center(
            rx.box(
                rx.vstack(
                    rx.heading("Cadastro do perfil", size="7"),
                    rx.text(
                        "Configure seus dados pessoais e objetivos para continuar sua rotina no Pulse.",
                        color="gray",
                    ),
                    rx.form(
                        rx.vstack(
                            rx.grid(
                                rx.vstack(
                                    field_label("Nome completo"),
                                    rx.input(
                                        placeholder="Ex.: Ana Souza",
                                        value=PerfilState.nome,
                                        on_change=lambda value: PerfilState.set_field("nome", value),
                                    ),
                                    width="100%",
                                ),
                                rx.vstack(
                                    field_label("Data de nascimento"),
                                    rx.input(
                                        type_="date",
                                        value=PerfilState.data_nascimento,
                                        on_change=lambda value: PerfilState.set_field("data_nascimento", value),
                                    ),
                                    width="100%",
                                ),
                                columns="2",
                                spacing="4",
                                width="100%",
                            ),
                            rx.grid(
                                rx.vstack(
                                    field_label("Sexo"),
                                    rx.select(
                                        ["Masculino", "Feminino"],
                                        value=PerfilState.sexo,
                                        on_change=lambda value: PerfilState.set_field("sexo", value),
                                        placeholder="Selecione",
                                        width="100%",
                                    ),
                                    width="100%",
                                ),
                                rx.vstack(
                                    field_label("Altura (cm)"),
                                    rx.input(
                                        type_="number",
                                        placeholder="170",
                                        value=PerfilState.altura_cm,
                                        on_change=lambda value: PerfilState.set_field("altura_cm", value),
                                    ),
                                    width="100%",
                                ),
                                columns="2",
                                spacing="4",
                                width="100%",
                            ),
                            rx.grid(
                                rx.vstack(
                                    field_label("Tipo físico"),
                                    rx.input(
                                        placeholder="Ex.: 24.5",
                                        value=PerfilState.tipo_fisico,
                                        on_change=lambda value: PerfilState.set_field("tipo_fisico", value),
                                    ),
                                    width="100%",
                                ),
                                rx.vstack(
                                    field_label("Nível físico"),
                                    rx.input(
                                        placeholder="Ex.: Iniciante",
                                        value=PerfilState.nivel_fisico,
                                        on_change=lambda value: PerfilState.set_field("nivel_fisico", value),
                                    ),
                                    width="100%",
                                ),
                                columns="2",
                                spacing="4",
                                width="100%",
                            ),
                            rx.grid(
                                rx.vstack(
                                    field_label("Modalidade favorita"),
                                    rx.select(
                                        [
                                            "Musculação",
                                            "Cardio",
                                            "Funcional",
                                            "Luta",
                                            "CrossFit",
                                            "Yoga",
                                            "Esportes de areia",
                                            "Pilates",
                                        ],
                                        value=PerfilState.modalidade_fav,
                                        on_change=lambda value: PerfilState.set_field("modalidade_fav", value),
                                        placeholder="Selecione",
                                        width="100%",
                                    ),
                                    width="100%",
                                ),
                                rx.vstack(
                                    field_label("Horário favorito de treino"),
                                    rx.input(
                                        type_="number",
                                        placeholder="18",
                                        value=PerfilState.horario_fav_de_treino,
                                        on_change=lambda value: PerfilState.set_field("horario_fav_de_treino", value),
                                    ),
                                    width="100%",
                                ),
                                columns="2",
                                spacing="4",
                                width="100%",
                            ),
                            rx.grid(
                                rx.vstack(
                                    field_label("Meta semanal"),
                                    rx.input(
                                        type_="number",
                                        placeholder="3",
                                        value=PerfilState.meta_semanal,
                                        on_change=lambda value: PerfilState.set_field("meta_semanal", value),
                                    ),
                                    width="100%",
                                ),
                                rx.vstack(
                                    field_label("Objetivo"),
                                    rx.select(
                                        [
                                            "Hipertrofia (ganho de massa muscular)",
                                            "Emagrecimento (perda de gordura)",
                                            "Melhorar condicionamento físico",
                                            "Preservação de saúde mental",
                                        ],
                                        value=PerfilState.objetivo,
                                        on_change=lambda value: PerfilState.set_field("objetivo", value),
                                        placeholder="Selecione",
                                        width="100%",
                                    ),
                                    width="100%",
                                ),
                                columns="2",
                                spacing="4",
                                width="100%",
                            ),
                            rx.box(
                                rx.checkbox(
                                    "Quero registrar medidas corporais",
                                    checked=PerfilState.medidas,
                                    on_change=lambda value: PerfilState.set_field("medidas", value),
                                ),
                                width="100%",
                            ),
                            rx.button(
                                "Salvar perfil",
                                type="submit",
                                size="3",
                                width="100%",
                                disabled=PerfilState.is_submitting,
                            ),
                            spacing="4",
                            width="100%",
                        ),
                        on_submit=PerfilState.submit,
                        width="100%",
                    ),
                    rx.cond(
                        PerfilState.feedback != "",
                        rx.box(
                            rx.text(
                                PerfilState.feedback,
                                color="white",
                                size="3",
                            ),
                            background_color=rx.cond(PerfilState.feedback_tipo == "success", "green", "red"),
                            border_radius="12px",
                            padding="12px 16px",
                            width="100%",
                        ),
                        rx.fragment(),
                    ),
                    spacing="6",
                    width="100%",
                ),
                background="white",
                border="1px solid #e5e7eb",
                box_shadow="0 18px 40px rgba(15, 23, 42, 0.08)",
                border_radius="28px",
                padding="32px",
                width="100%",
                max_width="980px",
            ),
        ),
        max_width="1200px",
        padding_y="6",
        min_height="100vh",
    )


app = rx.App()
app.add_page(index, route="/")
app.add_page(index, route="/cadastro")
