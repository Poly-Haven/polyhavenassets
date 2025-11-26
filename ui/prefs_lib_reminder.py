from .. import icons


def prefs_lib_reminder(self, context):
    def draw_warning(self, text, draw_save_btn=False, draw_import_method=False):
        row = self.layout.row(align=True)
        if context.preferences.active_section == "ADDONS":
            row.alignment = "CENTER"
        else:
            row.alignment = "RIGHT"
        i = icons.get_icons()
        row.label(text=text, icon_value=i["exclamation-triangle"].icon_id)

        if draw_save_btn:
            row.operator("wm.save_userpref", text="Save")

        if draw_import_method:
            row.prop(draw_import_method, "import_method", text="Import Method")

    for lib in context.preferences.filepaths.asset_libraries:
        if lib.name.lower() == "poly haven":
            if "APPEND" not in lib.import_method:
                draw_warning(
                    self,
                    "Import method should be set to 'Append', otherwise assets will not be editable.",
                    draw_import_method=lib,
                )
            if context.preferences.is_dirty:
                draw_warning(self, "Don't forget to save your preferences!", draw_save_btn=True)
            if context.preferences.active_section == "ADDONS":
                row = self.layout.row(align=True)
                row.alignment = "CENTER"
                row.label(text="Asset library location: " + lib.path, icon="CHECKMARK")
            return

    if context.preferences.active_section == "ADDONS":
        draw_warning(
            self,
            'No asset library named "Poly Haven", please create one in the File Paths tab on the left.',
        )
    else:
        draw_warning(self, 'Poly Haven: No asset library named "Poly Haven", please create it!')
