import bpy
import bmesh
import logging
import math
from mathutils import Vector
import numpy
from ..utils.is_ph_asset import is_ph_asset
from ..utils.tex_users import tex_users
from ..utils import mesh_helpers

log = logging.getLogger(__name__)


class PHA_OT_tex_scale_fix(bpy.types.Operator):
    bl_idname = "pha.tex_scale_fix"
    bl_label = "Fix Texture Scale"
    bl_description = (
        "Updates the material mapping node to suit the real world scale of this texture, "
        " relative to the average surface area of the meshes it is applied to"
    )
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(self, context):
        if not hasattr(context, "material"):
            return False

        self.asset_id = is_ph_asset(context, context.material)
        return bool(self.asset_id)

    def execute(self, context):
        objects = set(tex_users(context))

        # Force object mode, to ensure uv map is up to date
        obj_mode = bpy.context.active_object.mode
        if obj_mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        surface_areas = []
        uv_areas = []
        for obj in objects:
            if obj.scale != Vector((1, 1, 1)):
                self.report({"WARNING"}, f"{obj.name} has a non-uniform scale, texture scale will be incorrect.")

            # Get object surface area
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            object_surface_area = mesh_helpers.bmesh_calc_area(bm)
            surface_areas.append(object_surface_area)

            # Get UV area (0 - 1)
            # Thanks to Sietse for the help with some of this!
            # https://blender.stackexchange.com/questions/279479/how-to-calculate-the-total-uv-area-used
            uv_layer = bm.loops.layers.uv.active
            total_uv_area = 0
            for face in bm.faces:
                uv_verts = []
                for loop in face.loops:
                    uv_verts.append(loop[uv_layer].uv)
                face_uv_area = mesh_helpers.polygon_area(uv_verts)
                total_uv_area += face_uv_area
            uv_areas.append(total_uv_area)

        # Calculate multiplier
        tex_area = (context.material["Real Scale (mm)"][0] / 1000) * (context.material["Real Scale (mm)"][1] / 1000)
        aspect_ratio = context.material["Real Scale (mm)"][1] / context.material["Real Scale (mm)"][0]
        sqrt_aspect_ratio = math.sqrt(aspect_ratio)
        average_surface_area = numpy.mean(surface_areas)
        average_uv_area = numpy.mean(uv_areas)
        multiplier = math.sqrt(average_surface_area) / math.sqrt(tex_area) / math.sqrt(average_uv_area)
        log.debug(
            f"\nAvg surface area: {average_surface_area}"
            f"\nAvg UV area: {average_uv_area}"
            f"\nTex area: {tex_area}"
            f"\nMultiplier: {multiplier}"
        )

        # Scale texture using multiplier
        for node in context.material.node_tree.nodes:
            if node.type == "MAPPING":
                node.inputs["Scale"].default_value.x = multiplier * sqrt_aspect_ratio
                node.inputs["Scale"].default_value.y = multiplier / sqrt_aspect_ratio
        for obj in objects:
            for mod in obj.modifiers:
                if mod.type == "DISPLACE":
                    try:
                        img = mod.texture.image
                        if is_ph_asset(context, img):
                            mod.texture.crop_max_x = multiplier * sqrt_aspect_ratio
                            mod.texture.crop_max_y = multiplier / sqrt_aspect_ratio
                    except AttributeError:
                        log.debug("No image on displacement modifier")

        return {"FINISHED"}
