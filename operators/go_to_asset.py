import bpy
import logging

log = logging.getLogger(__name__)


class PHA_OT_go_to_asset(bpy.types.Operator):
    bl_idname = "pha.go_to_asset"
    bl_label = "Go to asset"
    bl_description = "View this asset"
    bl_options = {"INTERNAL"}

    asset: bpy.props.StringProperty()

    def execute(self, context):
        if context.space_data.params.filter_search == self.asset:
            # User might have clicked on the button twice, thinking it didn't work.
            self.report({"INFO"}, "If no asset is shown, try selecting the 'ALL' catalog.")
        context.space_data.params.filter_search = self.asset

        return {"FINISHED"}
