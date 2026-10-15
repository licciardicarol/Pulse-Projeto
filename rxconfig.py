import reflex as rx

config = rx.Config(
    app_name="projetofacul",
    # variáveis do Xano ficam no .env local (fora do Git); ver .env.example
    env_file=".env",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
        rx.plugins.RadixThemesPlugin(),
    ]
)