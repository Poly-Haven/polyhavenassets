import bpy
import logging
import math
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
        self.asset_id = is_ph_asset(context, context.material)
        return bool(self.asset_id)

    def execute(self, context):
        objects = set(tex_users(context))
        areas = []
        for obj in objects:
            bm = mesh_helpers.bmesh_copy_from_object(obj, apply_modifiers=True)
            area = mesh_helpers.bmesh_calc_area(bm)
            areas.append(area)
            log.debug(f"{obj.name} area: {area}")

        average_area = numpy.mean(areas)
        average_dimension = math.sqrt(average_area)
        multiplier = average_dimension / (context.material["Real Scale (mm)"][0] / 1000)
        log.debug(f"Average area: {average_area}, sqrt: {average_dimension}, multiplier: {multiplier}")

        for node in context.material.node_tree.nodes:
            if node.type == "MAPPING":
                node.inputs["Scale"].default_value = (multiplier, multiplier, multiplier)
        for obj in objects:
            for mod in obj.modifiers:
                if mod.type == "DISPLACE":
                    try:
                        img = mod.texture.image
                        if is_ph_asset(context, img):
                            mod.texture.crop_max_x = multiplier
                            mod.texture.crop_max_y = multiplier
                    except AttributeError:
                        log.debug("No image on displacement modifier")

        return {"FINISHED"}
