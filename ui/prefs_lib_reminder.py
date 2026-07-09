from .. import icons


def prefs_lib_reminder(self, context):
    i = icons.get_icons()
    is_addons_section = context.preferences.active_section == "ADDONS"
    box = None

    def get_box():
        nonlocal box
        if box is None:
            box = self.layout.box()
            header = box.row(align=True)
            if is_addons_section:
                header.alignment = "CENTER"
            header.label(text="", icon_value=i["polyhaven"].icon_id)
            header.label(text="Poly Haven")
        return box

    def draw_warning(text, draw_save_btn=False, draw_import_method=False):
        row = get_box().row(align=True)
        if is_addons_section:
            row.alignment = "CENTER"
        else:
            row.alignment = "RIGHT"
        row.label(text=text, icon_value=i["exclamation-triangle"].icon_id)

        if draw_save_btn:
            row.operator("wm.save_userpref", text="Save")

        if draw_import_method:
            row.prop(draw_import_method, "import_method", text="Import Method")

    for lib in context.preferences.filepaths.asset_libraries:
        if lib.name.lower() == "poly haven":
            if "APPEND" not in lib.import_method:
                draw_warning(
                    "Import method should be set to 'Append', otherwise assets will not be editable.",
                    draw_import_method=lib,
                )
            if context.preferences.is_dirty:
                draw_warning("Don't forget to save your preferences!", draw_save_btn=True)
            if is_addons_section:
                row = self.layout.row(align=True)
                row.alignment = "CENTER"
                row.label(text="Asset library location: " + lib.path, icon="CHECKMARK")
            return

    if is_addons_section:
        draw_warning(
            'No asset library named exactly "Poly Haven", please create one in the File Paths tab on the left.',
        )
    else:
        draw_warning('Poly Haven: No asset library named exactly "Poly Haven", please create it!')
