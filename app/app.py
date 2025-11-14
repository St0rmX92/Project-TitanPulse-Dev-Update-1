import reflex as rx
from app.components.sidebar import sidebar
from app.components.main_panel import main_panel
from app.states.debloat_state import DebloatState


def footer() -> rx.Component:
    return rx.el.footer(
        rx.el.p(
            "Copyright © 2025 Adan Alhasan",
            class_name=rx.cond(
                DebloatState.theme == "light",
                "text-xs text-gray-500",
                "text-xs text-gray-400",
            ),
        ),
        class_name="w-full text-center py-4",
    )


def index() -> rx.Component:
    return rx.el.main(
        rx.el.div(
            sidebar(),
            main_panel(),
            class_name=rx.cond(
                DebloatState.theme == "light",
                "flex flex-row h-screen w-screen bg-white overflow-hidden shadow-2xl rounded-2xl border border-purple-200",
                "flex flex-row h-screen w-screen bg-gray-900 overflow-hidden shadow-2xl rounded-2xl border border-purple-800",
            ),
        ),
        footer(),
        class_name=rx.cond(
            DebloatState.theme == "light",
            "font-['Lora'] bg-gray-100 min-h-screen flex flex-col items-center justify-center p-4",
            "font-['Lora'] bg-gray-950 min-h-screen flex flex-col items-center justify-center p-4",
        ),
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Lora:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index, on_load=DebloatState.on_load, route="/")