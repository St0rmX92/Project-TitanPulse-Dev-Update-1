import reflex.reflex as reflex

if __name__ == "__main__":
    refl_app = reflex.get_app()
    reflex.run(
        app_module=f"{refl_app.app_name}.{refl_app.app_name}:app",
        host="0.0.0.0",
        port=3000,
    )