import bpy
from ..utils.get_asset_lib import get_asset_lib


class PHA_OT_pull_from_polyhaven(bpy.types.Operator):
    bl_idname = "pha.pull_from_polyhaven"
    bl_label = "Pull from Poly Haven"
    bl_description = "Updates the local asset library with new assets from polyhaven.com"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):

        asset_lib = get_asset_lib(context)
        if asset_lib is None:
            self.report({'ERROR'}, "First open Preferences > File Paths and create an asset library named \"Poly Haven\"")
            return {'CANCELLED'}

        self.report({'INFO'}, asset_lib.name)
        return {'FINISHED'}
