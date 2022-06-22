import bpy


class PHA_OT_pull_from_polyhaven(bpy.types.Operator):
    bl_idname = "pha.pull_from_polyhaven"
    bl_label = "Pull from Poly Haven"
    bl_description = "Updates the local asset library with new assets from polyhaven.com"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        self.report({'INFO'}, "TODO")  # TODO
        return {'FINISHED'}
