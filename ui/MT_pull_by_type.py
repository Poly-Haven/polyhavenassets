import bpy


class PHA_MT_pull_by_type(bpy.types.Menu):
    bl_label = "Fetch only hdris/textures/models"
    bl_description = "Instead of downloading all assets, download only assets of a certain type"

    def draw(self, context):
        for asset_type in ["All", "HDRIs", "Textures", "Models"]:
            self.layout.operator("pha.pull_from_polyhaven", text=asset_type).asset_type = asset_type.lower()
