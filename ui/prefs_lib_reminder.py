from .. import icons


def prefs_lib_reminder(self, context):

    def draw_warning(self, text):
        row = self.layout.row(align=True)
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
            return
    draw_warning(self, "Poly Haven: No asset library named \"Poly Haven\", please create it!")
