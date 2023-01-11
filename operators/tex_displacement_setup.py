import bpy
from ..icons import get_icons
from ..utils.tex_users import tex_users
from ..utils.dpi_factor import dpi_factor
import logging

log = logging.getLogger(__name__)

# Displacement modes:
_ADAPTIVE = "Adaptive"
_STATIC = "Static"


class PHA_OT_tex_displacement_setup(bpy.types.Operator):
    bl_idname = "pha.tex_displacement_setup"
    bl_label = "Set up displacement"
    bl_description = (
        "Enable all render settings and create modifiers to get tessellation / micro-displacement "
        "working for this material"
    )
    bl_options = {"REGISTER", "UNDO"}

    displacement_method: bpy.props.EnumProperty(
        items=[
            (_ADAPTIVE, _ADAPTIVE, "Dynamically tessellate the mesh based on the camera distance"),
            (_STATIC, _STATIC, "Subdivide the mesh a specific number of times"),
        ],
        name="Displacement Method",
        default=_STATIC,
        description="",
    )
    displacement_subdivisions: bpy.props.IntProperty(
        name="Subdivisions",
        default=6,
        min=0,
        soft_max=6,
        description="Amount of subdivisions to use for the displacement modifier",
    )

    @classmethod
    def find_connected_by_type(self, node, node_type):
        """Find all nodes of the specified type that are connected to the inputs of the given node"""

        def recursive_search(node, node_type):
            for input in node.inputs:
                for link in input.links:
                    from_node = link.from_node
                    if from_node.type == node_type:
                        yield from_node
                    yield from recursive_search(from_node, node_type)

        return list(set(recursive_search(node, node_type)))

    @classmethod
    def setup_render_displacement(self, context):
        context.scene.cycles.feature_set = "EXPERIMENTAL"
        objects = tex_users(context)
        for obj in objects:
            obj.cycles.use_adaptive_subdivision = True
            needs_subsurf = True
            for mod in obj.modifiers:
                if mod.type == "SUBSURF":
                    needs_subsurf = False
                    break
            if needs_subsurf:
                mod = obj.modifiers.new("Tessellation", "SUBSURF")
                mod.subdivision_type = "SIMPLE"

        return {"FINISHED"}

    @classmethod
    def setup_mesh_displacement(self, context, subdivisions=6):
        """Add subdiv & a displacement modifiers to *physically* displace the mesh"""
        objects = tex_users(context)
        material: bpy.types.Material = context.material
        material.cycles.displacement_method = "BUMP"
        bl_texture: bpy.types.ImageTexture = context.blend_data.textures.new(material.name + "_disp", "IMAGE")
        bl_texture.use_alpha = False

        # Get displacement texture from material
        output_type_map = {
            "CYCLES": "CYCLES",
            "BLENDER_EEVEE": "EEVEE",
        }
        active_output = material.node_tree.get_output_node(output_type_map[context.scene.render.engine])
        displacement_node = self.find_connected_by_type(active_output, "DISPLACEMENT")[0]
        if not displacement_node:
            self.report({"ERROR"}, "No displacement node found")
            return {"CANCELLED"}
        midlevel = displacement_node.inputs["Midlevel"].default_value
        strength = displacement_node.inputs["Scale"].default_value
        bl_texture.image = displacement_node.inputs["Height"].links[0].from_node.image
        # Fix scale
        mapping_node = self.find_connected_by_type(active_output, "MAPPING")[0]
        if not mapping_node:
            self.report({"ERROR"}, "No mapping node found")
            return {"CANCELLED"}
        applied_scale = mapping_node.inputs["Scale"].default_value
        bl_texture.crop_max_x = applied_scale[0]
        bl_texture.crop_max_y = applied_scale[1]

        for obj in objects:
            needs_subsurf = True
            for mod in obj.modifiers:
                if mod.type == "SUBSURF":
                    needs_subsurf = False
                    break
            if needs_subsurf:
                mod = obj.modifiers.new("Tessellation", "SUBSURF")
                mod.subdivision_type = "SIMPLE"
                mod.levels = subdivisions
                mod.render_levels = subdivisions

            needs_displacement = True
            for mod in obj.modifiers:
                if mod.type == "DISPLACE":
                    needs_displacement = False
                    break
            if needs_displacement:
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
            row = col.row()
            row.label(text="Displacement Method:")
            row.prop(self, "displacement_method", expand=True)
        col.separator()

        col.label(text="Warning:", icon_value=icons["exclamation-triangle"].icon_id)
        if self.displacement_method == _ADAPTIVE:
            col.label(text="This will enable the Experimental Feature Set, and add")
            col.label(text="adaptive Subsurf modifiers to objects using this material.")
            col.label(text="The displacement will NOT be visible in EEVEE.")
        elif self.displacement_method == _STATIC:
            col.label(text="This will add a Subsurf modifier and a Displacement modifier")
            col.label(text="to objects using this material.")
            col.label(text="This could freeze your computer for high-poly objects.")

        if self.displacement_method == _STATIC:
            col.prop(self, "displacement_subdivisions")

    def invoke(self, context, event):
        self.displacement_method = _ADAPTIVE if context.scene.render.engine == "CYCLES" else _STATIC
        return context.window_manager.invoke_props_dialog(self, width=round(350 * dpi_factor()))

    def execute(self, context):
        if self.displacement_method == _ADAPTIVE:
            return self.setup_render_displacement(context)
        elif self.displacement_method == _STATIC:
            return self.setup_mesh_displacement(context, subdivisions=self.displacement_subdivisions)
