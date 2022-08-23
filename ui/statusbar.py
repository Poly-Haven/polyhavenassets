from ..icons import get_icons


def ui(self, context, statusbar=True):
    props = context.window_manager.pha_props
    if props.progress_total:
        row = self.layout.row(align=True)
        row.prop(
            props,
            "progress_percent",
            text="Cancelling..." if props.progress_cancel else props.progress_word,
            slider=True,
        )
        if not props.progress_cancel:
            row.operator("pha.cancel_download", text="", icon="CANCEL")
        if statusbar:
            icons = get_icons()
            self.layout.label(text="", icon_value=icons["polyhaven"].icon_id)
        else:
            self.layout.separator()  # Space at end
