import bpy
from ..utils.is_ph_asset import is_ph_asset
from ..icons import get_icons


class PHA_PT_asset_texture:

    asset_id = ""

    @classmethod
    def poll(self, context):
        self.asset_id = is_ph_asset(context, context.material)
        return bool(self.asset_id)

    def draw_header(self, context):
        icons = get_icons()
        self.layout.label(text=f"Asset: {self.asset_id}", icon_value=icons["polyhaven"].icon_id)

    def draw(self, context):
        layout = self.layout

        col = layout.column()
        col.operator("pha.tex_scale_fix")


class PHA_PT_asset_texture_eevee(bpy.types.Panel, PHA_PT_asset_texture):
    bl_label = " "
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"
    bl_parent_id = "EEVEE_MATERIAL_PT_context_material"


class PHA_PT_asset_texture_cycles(bpy.types.Panel, PHA_PT_asset_texture):
    bl_label = " "
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"
    bl_parent_id = "CYCLES_PT_context_material"
