from ..icons import get_icons


def ui(self, context, statusbar=True):
    if context.window_manager.pha_props.progress_total:
        self.layout.prop(
            context.window_manager.pha_props,
            "progress_percent",
            text=context.window_manager.pha_props.progress_word,
            slider=True,
        )
        if statusbar:
            icons = get_icons()
            self.layout.label(text="", icon_value=icons["polyhaven"].icon_id)
        else:
            self.layout.separator()
