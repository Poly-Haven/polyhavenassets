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
    displacement_method: bpy.props.EnumProperty(items = [("Render", "Render", "Let the render engine displace"), ("Modifier", "Modifier", "Use the Displacement Modifier")], name="Displacement Method", default="Modifier", description="")
    displacement_subdivisions: bpy.props.IntProperty(name="Subdivisions", default=6, min=0, soft_max=6, description="Amount of subdivisions to use for the displacement modifier")

    @classmethod
    def setup_render_displacement(self, context):
        context.scene.cycles.feature_set = "EXPERIMENTAL"
        context.material.cycles.displacement_method = "DISPLACEMENT"
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

    @classmethod
    def setup_mesh_displacement(self, context, subdivisions = 6):
        """Add subdiv & a displacement modifiers to *physically* displace the mesh"""
        objects = tex_users(context)
        material: bpy.types.Material = context.material
        material.cycles.displacement_method = "BUMP"
        bl_texture: bpy.types.ImageTexture = context.blend_data.textures.new(material.name + "_disp", "IMAGE")
        bl_texture.use_alpha = False

        nodes = material.node_tree.nodes
        # Get displacement texture from material (assumes node tree has "Displacement" node)
        displacement = nodes["Displacement"]
        midlevel = displacement.inputs["Midlevel"].default_value
        strength = displacement.inputs["Scale"].default_value
        bl_texture.image = displacement.inputs["Height"].links[0].from_node.image
        # Fix scale
        applied_scale = nodes["Mapping"].inputs["Scale"].default_value
        bl_texture.crop_max_x = applied_scale[0]
        bl_texture.crop_max_y = applied_scale[1]

        for obj in objects:
            needs_subsurf = True
            for mod in obj.modifiers:  # Reverse so we only act on the last subsurf
                if mod.type == "SUBSURF":
                    needs_subsurf = False
                    break
            if needs_subsurf:
                mod = obj.modifiers.new("Tessellation", "SUBSURF")
                mod.subdivision_type = "SIMPLE"
                mod.levels = subdivisions
                mod.render_levels = subdivisions
            
            mod = obj.modifiers.new("Displacement", "DISPLACE")
            mod.texture_coords = "UV"
            mod.texture = bl_texture
            mod.mid_level = midlevel
            mod.strength = strength
    
        return {"FINISHED"}
    
    def draw(self, context):
        icons = get_icons()
        layout = self.layout
        col = layout.column(align=True)
        if context.scene.render.engine == "CYCLES":
            self.displacement_method = "Render"
            col.prop_tabs_enum(self, "displacement_method")
            col.separator()
        col.label(text="Warning:", icon_value=icons["exclamation-triangle"].icon_id)
        if self.displacement_method == "Render":
            col.label(text="This will enable the Experimental Feature Set, and add")
            col.label(text="adaptive Subsurf modifiers to objects using this material.")
        elif self.displacement_method == "Modifier":
            col.label(text="This will add a Subsurf modifier and a Displacement modifier")
            col.label(text="to objects using this material.")
            col.label(text="This could freeze your computer for high-poly objects.")
        col.separator()

        if self.displacement_method == "Modifier":
            col.prop(self, "displacement_subdivisions")
            col.separator()

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=round(350 * dpi_factor()))

    @classmethod
    def poll(self, context):
        return True

    def execute(self, context):
        if self.displacement_method == "Render":
            return self.setup_render_displacement(context)
        elif self.displacement_method == "Modifier":
            return self.setup_mesh_displacement(context, subdivisions=self.displacement_subdivisions)
