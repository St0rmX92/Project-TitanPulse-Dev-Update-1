import reflex as rx
from app.states.debloat_state import DebloatState


def sidebar_header() -> rx.Component:
    return rx.el.div(
        rx.icon("rocket", class_name="w-8 h-8 stroke-purple-500"),
        rx.el.h1(
            "TitanPulse",
            class_name=rx.cond(
                DebloatState.theme == "light",
                "text-2xl font-bold text-gray-800 tracking-tight",
                "text-2xl font-bold text-gray-100 tracking-tight",
            ),
        ),
        class_name=rx.cond(
            DebloatState.theme == "light",
            "flex items-center gap-3 p-4 border-b border-purple-100",
            "flex items-center gap-3 p-4 border-b border-purple-900",
        ),
    )


def option_toggle(
    icon: str, name: str, is_checked: rx.Var[bool], on_toggle: rx.event.EventSpec
) -> rx.Component:
    return rx.el.label(
        rx.icon(
            icon,
            class_name=rx.cond(
                DebloatState.theme == "light",
                "w-5 h-5 text-gray-500",
                "w-5 h-5 text-gray-400",
            ),
        ),
        rx.el.span(
            name,
            class_name=rx.cond(
                DebloatState.theme == "light",
                "flex-grow font-medium text-gray-700 text-sm",
                "flex-grow font-medium text-gray-300 text-sm",
            ),
        ),
        rx.el.div(
            rx.el.div(
                class_name=rx.cond(
                    is_checked,
                    "absolute left-0.5 top-0.5 h-5 w-5 rounded-full transition-transform duration-200 ease-in-out translate-x-5 bg-white shadow-sm",
                    "absolute left-0.5 top-0.5 h-5 w-5 rounded-full transition-transform duration-200 ease-in-out translate-x-0 bg-white shadow-sm",
                )
            ),
            class_name=rx.cond(
                is_checked,
                "relative w-11 h-6 rounded-full bg-gradient-to-r from-orange-500 to-orange-400 transition-colors",
                rx.cond(
                    DebloatState.theme == "light",
                    "relative w-11 h-6 rounded-full bg-gray-300 transition-colors",
                    "relative w-11 h-6 rounded-full bg-gray-600 transition-colors",
                ),
            ),
        ),
        rx.el.input(
            type="checkbox",
            checked=is_checked,
            on_change=on_toggle,
            class_name="sr-only",
        ),
        class_name=rx.cond(
            DebloatState.theme == "light",
            "flex items-center gap-4 px-4 py-2 rounded-lg hover:bg-purple-50 cursor-pointer",
            "flex items-center gap-4 px-4 py-2 rounded-lg hover:bg-gray-800 cursor-pointer",
        ),
    )


def category_section(category: rx.Var[dict]) -> rx.Component:
    category_id = category["id"]
    is_collapsed = DebloatState.collapsed_categories[category_id]
    return rx.el.div(
        rx.el.button(
            rx.el.div(
                rx.icon(
                    category["icon"],
                    class_name=rx.cond(
                        DebloatState.theme == "light",
                        "w-5 h-5 mr-3 text-purple-700",
                        "w-5 h-5 mr-3 text-purple-300",
                    ),
                ),
                rx.el.span(" ", category["name"], class_name="font-semibold"),
                class_name="flex items-center",
            ),
            rx.icon(
                "chevron-down",
                class_name=rx.cond(
                    is_collapsed,
                    "w-5 h-5 transition-transform duration-300",
                    "w-5 h-5 transition-transform duration-300 rotate-180",
                ),
            ),
            on_click=DebloatState.toggle_category(category_id),
            class_name=rx.cond(
                DebloatState.theme == "light",
                "w-full flex items-center justify-between p-3 text-sm text-purple-900 bg-purple-100 rounded-lg hover:bg-purple-200 transition-colors",
                "w-full flex items-center justify-between p-3 text-sm text-purple-100 bg-purple-900/50 rounded-lg hover:bg-purple-800/70 transition-colors",
            ),
        ),
        rx.el.div(
            rx.foreach(
                category["options"],
                lambda option: option_toggle(
                    option["icon"],
                    option["name"],
                    DebloatState.option_states[option["id"]],
                    DebloatState.toggle_option(option["id"]),
                ),
            ),
            class_name=rx.cond(
                is_collapsed,
                "overflow-hidden transition-all duration-300 ease-in-out max-h-0",
                "overflow-hidden transition-all duration-500 ease-in-out max-h-[1000px] pt-2",
            ),
        ),
        class_name="px-4 py-2",
    )


def sidebar() -> rx.Component:
    return rx.el.aside(
        sidebar_header(),
        rx.el.div(
            rx.foreach(DebloatState.debloat_categories, category_section),
            class_name="flex-grow overflow-y-auto py-4 space-y-2",
        ),
        class_name=rx.cond(
            DebloatState.theme == "light",
            "w-96 h-screen bg-gradient-to-b from-purple-50 to-white border-r border-purple-100 flex flex-col shadow-lg font-['Lora']",
            "w-96 h-screen bg-gradient-to-b from-gray-900 to-gray-800 border-r border-purple-900 flex flex-col shadow-lg font-['Lora']",
        ),
    )