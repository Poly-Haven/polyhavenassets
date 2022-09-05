import bpy
import logging

log = logging.getLogger(__name__)


class PHA_OT_cancel_download(bpy.types.Operator):
    bl_idname = "pha.cancel_download"
    bl_label = "Cancel download"
    bl_description = "Cancels the current download operation"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        context.window_manager.pha_props.progress_cancel = True

        return {"FINISHED"}
