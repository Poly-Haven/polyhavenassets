from .. import icons


def ui(self, context):

    if context.space_data.params.asset_library_ref != "Poly Haven":
        return

    layout = self.layout
    row = layout.row()
    row.alignment = "RIGHT"
    i = icons.get_icons()
    row.operator("pha.pull_from_polyhaven", text="Fetch Assets", icon_value=i["polyhaven"].icon_id)
