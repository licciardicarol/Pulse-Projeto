from pathlib import Path

import reflex as rx

config = rx.Config(
    app_name="projetofacul",
    # variáveis do Xano ficam no .env local (fora do Git); ver .env.example.
    # Caminho absoluto: o backend do `reflex run` pode rodar com outra pasta de trabalho.
    env_file=str(Path(__file__).resolve().parent / ".env"),
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
        # destaque azul do projeto nos componentes Radix (no lugar do ciano padrão)
        rx.plugins.RadixThemesPlugin(theme=rx.theme(appearance="dark", accent_color="blue")),
    ]
)