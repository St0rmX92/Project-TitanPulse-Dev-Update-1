import reflex as rx
from app.states.debloat_state import DebloatState


def theme_toggle() -> rx.Component:
    return rx.el.div(
        rx.el.span(
            "Tema",
            class_name=rx.cond(
                DebloatState.theme == "light",
                "text-sm font-medium text-gray-700",
                "text-sm font-medium text-gray-300",
            ),
        ),
        rx.el.button(
            rx.icon(
                "sun",
                class_name=rx.cond(
                    DebloatState.theme == "light",
                    "h-5 w-5 text-orange-400",
                    "h-5 w-5 text-gray-500",
                ),
            ),
            rx.el.div(
                rx.el.div(
                    class_name=rx.cond(
                        DebloatState.theme == "light",
                        "h-5 w-5 rounded-full bg-white shadow-md transform transition-transform duration-300 translate-x-0",
                        "h-5 w-5 rounded-full bg-white shadow-md transform transition-transform duration-300 translate-x-6",
                    )
                ),
                class_name=rx.cond(
                    DebloatState.theme == "light",
                    "w-12 h-6 flex items-center rounded-full bg-gray-200",
                    "w-12 h-6 flex items-center rounded-full bg-purple-600",
                ),
            ),
            rx.icon(
                "moon",
                class_name=rx.cond(
                    DebloatState.theme == "light",
                    "h-5 w-5 text-gray-400",
                    "h-5 w-5 text-purple-300",
                ),
            ),
            on_click=DebloatState.toggle_theme,
            class_name="flex items-center gap-2 px-1",
        ),
        class_name="flex items-center justify-between mt-6",
    )


def log_view() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Log in Tempo Reale",
            class_name=rx.cond(
                DebloatState.theme == "light",
                "text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3",
                "text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3",
            ),
        ),
        rx.el.div(
            rx.foreach(
                DebloatState.log_output,
                lambda log: rx.el.p(
                    log,
                    class_name=rx.cond(
                        DebloatState.theme == "light",
                        "font-mono text-sm text-gray-600 leading-relaxed",
                        "font-mono text-sm text-gray-300 leading-relaxed",
                    ),
                ),
            ),
            id="log-area",
            class_name=rx.cond(
                DebloatState.theme == "light",
                "h-full p-4 bg-gray-50 rounded-lg overflow-y-auto border border-gray-200",
                "h-full p-4 bg-gray-800 rounded-lg overflow-y-auto border border-gray-700",
            ),
        ),
        class_name="flex flex-col h-full",
    )


def main_panel() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "Pannello di Controllo",
            class_name=rx.cond(
                DebloatState.theme == "light",
                "text-3xl font-bold text-gray-800 mb-6",
                "text-3xl font-bold text-gray-100 mb-6",
            ),
        ),
        rx.el.div(
            rx.el.p(
                "Progresso",
                class_name=rx.cond(
                    DebloatState.theme == "light",
                    "text-sm font-semibold text-gray-600",
                    "text-sm font-semibold text-gray-400",
                ),
            ),
            rx.el.p(
                f"{DebloatState.progress}%",
                class_name="text-sm font-bold text-purple-500",
            ),
            class_name="flex justify-between items-center mb-2",
        ),
        rx.el.div(
            rx.el.div(
                style={"width": DebloatState.progress.to_string() + "%"},
                class_name="h-full bg-gradient-to-r from-purple-500 to-orange-500 rounded-full transition-all duration-300 ease-in-out",
            ),
            class_name=rx.cond(
                DebloatState.theme == "light",
                "w-full bg-gray-200 rounded-full h-2.5 mb-8 shadow-inner",
                "w-full bg-gray-700 rounded-full h-2.5 mb-8 shadow-inner",
            ),
        ),
        rx.el.button(
            rx.icon("zap", class_name="mr-2"),
            "Avvia Ottimizzazione",
            on_click=DebloatState.start_debloat,
            disabled=DebloatState.is_running,
            class_name="w-full flex items-center justify-center p-4 rounded-xl bg-gradient-to-r from-purple-600 to-orange-500 text-white font-bold text-lg shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:from-purple-400 disabled:to-orange-300",
        ),
        theme_toggle(),
        rx.el.div(
            class_name=rx.cond(
                DebloatState.theme == "light",
                "my-8 border-t border-gray-200",
                "my-8 border-t border-gray-700",
            )
        ),
        log_view(),
        class_name=rx.cond(
            DebloatState.theme == "light",
            "flex-1 p-8 bg-white",
            "flex-1 p-8 bg-gray-900",
        ),
    )