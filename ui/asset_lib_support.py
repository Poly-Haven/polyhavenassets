from .. import icons


def ui(self, context):

    lib_ref = getattr(context.space_data.params, "asset_library_ref", None)  # Blender < 4.0
    lib_ref = getattr(context.space_data.params, "asset_library_reference", lib_ref)  # Blender > 4.0
    if lib_ref.lower() != "poly haven":
        return

    layout = self.layout
    row = layout.row()
    row.alignment = "RIGHT"
    i = icons.get_icons()
    row.operator(
        "wm.url_open", text="Support us!", icon_value=i["polyhaven"].icon_id
    ).url = "https://www.patreon.com/polyhaven/overview"
