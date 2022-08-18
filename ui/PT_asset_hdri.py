import bpy
from ..utils.is_ph_asset import is_ph_asset
from ..icons import get_icons


class PHA_PT_asset_hdri(bpy.types.Panel):

    bl_label = " "
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "world"
    bl_parent_id = "WORLD_PT_context_world"

    asset_id = ""

    @classmethod
    def poll(self, context):
        self.asset_id = is_ph_asset(context, context.object.instance_collection)
        return bool(self.asset_id)

    def draw_header(self, context):
        icons = get_icons()
        self.layout.label(text=f"Asset: {self.asset_id}", icon_value=icons["polyhaven"].icon_id)

    def draw(self, context):
        layout = self.layout

        col = layout.column()
        col.label(text="Test!")
