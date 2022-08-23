import bpy
import textwrap
from .. import icons
from ..utils.dpi_factor import dpi_factor
from ..utils.early_access import early_access


def paragraph(paragraph, width, layout):
    wrapp = textwrap.TextWrapper(width=round(width / 6.5))
    wList = wrapp.wrap(text=paragraph)
    layout.separator()
    textcol = layout.column(align=True)
    textcol.scale_y = 0.7
    for text in wList:
        row = textcol.row(align=True)
        row.alignment = "CENTER"
        row.label(text=text)


class PHA_PT_sidebar(bpy.types.Panel):

    bl_label = "Poly Haven"
    bl_space_type = "FILE_BROWSER"
    bl_region_type = "TOOLS"
    bl_options = {"HIDE_HEADER"}

    @classmethod
    def poll(self, context):
        return context.area.ui_type == "ASSETS" and context.space_data.params.asset_library_ref == "Poly Haven"

    def draw(self, context):
        if not early_access:  # We don't need to nag existing supporters :)
            layout = self.layout
            i = icons.get_icons()
            col = layout.column()
            sidebar_width = 10000
            for region in context.area.regions:
                if region.type == "TOOLS":
                    sidebar_width = region.width / dpi_factor()
            row = col.row()
            row.alignment = "CENTER"
            row.scale_y = 1.5
            row.operator(
                "wm.url_open", text="Support us!", icon_value=i["heart"].icon_id
            ).url = "https://www.patreon.com/polyhaven/overview"
            paragraph(
                (
                    "You might have downloaded this add-on for free, but Poly Haven needs funds to continue "
                    "creating assets for you :)"
                ),
                sidebar_width,
                col,
            )
            paragraph(
                (
                    "Please support our work by purchasing this add-on on the "
                    "Blender Market or by supporting us on Patreon."
                ),
                sidebar_width,
                col,
            )
            col.separator()
