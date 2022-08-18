import bpy
from ..icons import get_icons
from ..utils.tex_users import tex_users
from ..utils.dpi_factor import dpi_factor
import logging

log = logging.getLogger(__name__)


class PHA_OT_tex_displacement_setup(bpy.types.Operator):
    bl_idname = "pha.tex_displacement_setup"
    bl_label = "Set up displacement"
    bl_description = (
        "Enable all render settings and create modifiers to get tessellation / micro-displacement "
        "working for this material"
    )
    bl_options = {"REGISTER", "UNDO"}

    def draw(self, context):
        icons = get_icons()
        layout = self.layout
        col = layout.column(align=True)
        col.label(text="Warning:", icon_value=icons["exclamation-triangle"].icon_id)
        col.label(text="This will enable the Experimental Feature Set, and add")
        col.label(text="adaptive Subsurf modifiers to objects using this material.")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=round(300 * dpi_factor()))

    @classmethod
    def poll(self, context):
        if context.scene.render.engine != "CYCLES":
            return False
        return True

    def execute(self, context):
        context.scene.cycles.feature_set = "EXPERIMENTAL"
        objects = tex_users(context)
        for obj in objects:
            obj.cycles.use_adaptive_subdivision = True
            needs_subsurf = True
            for mod in obj.modifiers:  # Reverse so we only act on the last subsurf
                if mod.type == "SUBSURF":
                    needs_subsurf = False
                    break
            if needs_subsurf:
                mod = obj.modifiers.new("Tessellation", "SUBSURF")
                mod.subdivision_type = "SIMPLE"

        return {"FINISHED"}
