from ..icons import get_icons


def ui(self, context):
    if context.window_manager.pha_props.progress_total:
        icons = get_icons()
        self.layout.prop(
            context.window_manager.pha_props,
            "progress_percent",
            text=context.window_manager.pha_props.progress_word,
            slider=True,
        )
        self.layout.label(text="", icon_value=icons["polyhaven"].icon_id)
