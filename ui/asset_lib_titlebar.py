from .. import icons


def ui(self, context):

    if context.space_data.params.asset_library_ref != "Poly Haven":
        return

    props = context.window_manager.pha_props
    layout = self.layout
    row = layout.row()
    row.alignment = "RIGHT"
    i = icons.get_icons()
    row.operator(
        "pha.pull_from_polyhaven",
        text=(
            "Downloading..."
            if props.progress_total != 0
            else (
                f"Fetch {props.new_assets} new asset{'s' if props.new_assets != 1 else ''}"
                if props.new_assets
                else "Fetch Assets"
            )
        ),
        icon_value=i["polyhaven"].icon_id,
    )
