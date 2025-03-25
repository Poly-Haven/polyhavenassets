from .. import icons


def ui(self, context):

    lib_ref = getattr(context.space_data.params, "asset_library_reference", None)
    if lib_ref.lower() != "poly haven":
        return

    props = context.window_manager.pha_props
    layout = self.layout
    sub = layout.row()
    row = sub.row(align=True)
    row.use_property_split = True
    i = icons.get_icons()
    op = row.operator(
        "pha.pull_from_polyhaven",
        text=(
            "Busy..."
            if props.progress_total != 0
            else (
                f"Fetch {props.new_assets} new asset{'s' if props.new_assets != 1 else ''}"
                if props.new_assets
                else "Fetch Assets"
            )
        ),
        icon_value=i["polyhaven"].icon_id,
    )
    op.asset_type = "all"
    op.revalidate = False
    b = row.box()  # Force some kind of emboss effect
    b.menu("PHA_MT_pull_by_type", text="", icon="DOWNARROW_HLT")
