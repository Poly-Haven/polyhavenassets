from .. import icons


def panel(self, context):

    if context.space_data.params.asset_library_ref != "Poly Haven":
        return

    layout = self.layout
    row = layout.row()
    row.alignment = "RIGHT"
    i = icons.get_icons()
    row.operator(
        "wm.url_open", text="Support us!", icon_value=i["polyhaven"].icon_id
    ).url = "https://www.patreon.com/polyhaven/overview"
