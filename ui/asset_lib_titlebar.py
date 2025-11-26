import bpy
from .. import icons


def ui(self, context):

    lib_ref = getattr(context.space_data.params, "asset_library_ref", None)  # Blender < 4.0
    lib_ref = getattr(context.space_data.params, "asset_library_reference", lib_ref)  # Blender > 4.0
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
            "Needs Blender 3.2+"
            if bpy.app.version_string < "3.2.0"
            else (
                "Busy..."
                if props.progress_total != 0
                else (
                    f"Fetch {props.new_assets} new asset{'s' if props.new_assets != 1 else ''}"
                    if props.new_assets
                    else "Fetch Assets"
                )
            )
        ),
        icon_value=i["polyhaven"].icon_id,
    )
    op.asset_type = "all"
    op.revalidate = False
    b = row.box()  # Force some kind of emboss effect
    b.menu("PHA_MT_pull_by_type", text="", icon="DOWNARROW_HLT")

    import_method = context.space_data.params.import_method
    if import_method == "FOLLOW_PREFS":
        try:
            import_method = context.preferences.filepaths.asset_libraries[lib_ref].import_method
        except KeyError:
            # Library not found, shit's gonna break some other way!
            import_method = "APPEND"
    if "APPEND" not in import_method:
        row.separator_spacer()
        row.label(
            text="Import method is not 'Append', assets will not be editable.",
            icon_value=i["exclamation-triangle"].icon_id,
        )
        row.operator("wm.url_open", text="More info", icon="HELP").url = (
            "https://docs.polyhaven.com/en/guides/blender-addon#i-imported-an-asset-but-there-is-no-panel-to-change-resolutions-or-set-up-displacementscale"
        )
