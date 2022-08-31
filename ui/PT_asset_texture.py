import bpy
import logging
from ..utils.is_ph_asset import is_ph_asset
from ..icons import get_icons
from ..ui import statusbar
from ..ui import asset_info_box
from ..utils.get_asset_info import get_asset_info

log = logging.getLogger(__name__)

# Stored globally to avoid fetching data on every redraw
ASSET_INFO = {}


class PHA_PT_asset_texture:
    bl_label = " "
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"
    bl_options = {"HEADER_LAYOUT_EXPAND", "DEFAULT_CLOSED"}

    asset_id = ""

    @classmethod
    def poll(self, context):
        self.asset_id = is_ph_asset(context, context.material)
        if not self.asset_id:
            return False

        global ASSET_INFO
        if self.asset_id not in ASSET_INFO:
            log.debug(f"GETTING ASSET INFO {self.asset_id}")
            ASSET_INFO[self.asset_id] = get_asset_info(context, self.asset_id)
        return ASSET_INFO[self.asset_id]["type"] == 1

    def draw_header(self, context):
        icons = get_icons()
        row = self.layout.row()
        row.label(text=f"Asset: {self.asset_id}", icon_value=icons["polyhaven"].icon_id)
        sub = row.row(align=True)
        sub.alignment = "RIGHT"
        if context.window_manager.pha_props.progress_total != 0:
            statusbar.ui(self, context, statusbar=False)
        else:
            sub.menu(
                "PHA_MT_resolution_switch_texture",
                text=(context.material["res"] if "res" in context.material else "1k").upper(),
            )
            row.separator()  # Space at end

    def draw(self, context):
        layout = self.layout

        col = layout.column()
        row = col.row()
        row.operator("pha.tex_scale_fix", icon="CON_SIZELIMIT")
        row.operator("pha.tex_displacement_setup", icon="BRUSH_FILL")
        asset_info_box.draw(self, context, col, self.asset_id)


class PHA_PT_asset_texture_eevee(bpy.types.Panel, PHA_PT_asset_texture):
    bl_parent_id = "EEVEE_MATERIAL_PT_context_material"


class PHA_PT_asset_texture_cycles(bpy.types.Panel, PHA_PT_asset_texture):
    bl_parent_id = "CYCLES_PT_context_material"
