from .. import icons


def prefs_lib_reminder(self, context):

    def draw_warning(self, text):
        row = self.layout.row(align=True)
        if context.preferences.active_section == 'ADDONS':
            row.alignment = 'CENTER'
        else:
            row.alignment = 'RIGHT'
        i = icons.get_icons()
        row.label(
            text=text,
            icon_value=i['exclamation-triangle'].icon_id
        )

    for l in context.preferences.filepaths.asset_libraries:
        if l.name == "Poly Haven":
            if context.preferences.is_dirty:
                draw_warning(self, "Don't forget to save your preferences!")
            if context.preferences.active_section == 'ADDONS':
                row = self.layout.row(align=True)
                row.alignment = 'CENTER'
                row.label(
                    text="Asset library location: " + l.path,
                    icon='CHECKMARK'
                )
            return

    if context.preferences.active_section == 'ADDONS':
        draw_warning(self, "No asset library named \"Poly Haven\", please create one in the File Paths tab on the left.")
    else:
        draw_warning(self, "Poly Haven: No asset library named \"Poly Haven\", please create it!")
