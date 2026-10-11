import bpy
import bmesh
import logging
import math
from ..utils.is_ph_asset import is_ph_asset
from ..utils.tex_users import tex_users
from ..utils import box_mapping

log = logging.getLogger(__name__)

UV_EPSILON = 1e-5


def _world_area(face, matrix):
    """Area of a face after applying the object's transform (Newell's method)"""
    points = [matrix @ v.co for v in face.verts]
    normal = points[-1].cross(points[0])
    for a, b in zip(points, points[1:]):
        normal += a.cross(b)
    return normal.length / 2


def _uv_area(face, uv_layer):
    uvs = [loop[uv_layer].uv for loop in face.loops]
    twice_area = 0
    for i, a in enumerate(uvs):
        b = uvs[(i + 1) % len(uvs)]
        twice_area += a.x * b.y - b.x * a.y
    return abs(twice_area) / 2


def _same_uv(a, b):
    return abs(a.x - b.x) < UV_EPSILON and abs(a.y - b.y) < UV_EPSILON


def uv_islands(faces, uv_layer):
    """Group faces into islands: faces sharing an edge whose UVs match on both sides"""
    faces = list(faces)
    face_ids = {face: i for i, face in enumerate(faces)}
    parent = list(range(len(faces)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for face, i in face_ids.items():
        for loop in face.loops:
            a1, a2 = loop[uv_layer].uv, loop.link_loop_next[uv_layer].uv
            for other in loop.edge.link_loops:
                j = face_ids.get(other.face)
                if j is None or j == i:
                    continue
                b1, b2 = other[uv_layer].uv, other.link_loop_next[uv_layer].uv
                if other.vert == loop.vert:
                    connected = _same_uv(a1, b1) and _same_uv(a2, b2)
                else:
                    connected = _same_uv(a1, b2) and _same_uv(a2, b1)
                if connected:
                    parent[find(i)] = find(j)

    islands = {}
    for face, i in face_ids.items():
        islands.setdefault(find(i), []).append(face)
    return list(islands.values())


def scale_islands(bm, faces, uv_layer, matrix, size_m):
    """Scale each UV island so one UV unit covers size_m (width, height) of real-world surface.

    Returns the number of islands scaled.
    """
    count = 0
    for island in uv_islands(faces, uv_layer):
        world_area = sum(_world_area(f, matrix) for f in island)
        uv_area = sum(_uv_area(f, uv_layer) for f in island)
        if world_area <= 0 or uv_area <= 0:
            continue
        # Make 1 UV unit = 1 m, then fit the texture's aspect ratio
        k = math.sqrt(world_area / uv_area)
        scale_u, scale_v = k / size_m[0], k / size_m[1]

        loops = [loop for f in island for loop in f.loops]
        us = [loop[uv_layer].uv.x for loop in loops]
        vs = [loop[uv_layer].uv.y for loop in loops]
        center_u, center_v = (min(us) + max(us)) / 2, (min(vs) + max(vs)) / 2
        for loop in loops:
            uv = loop[uv_layer].uv
            uv.x = center_u + (uv.x - center_u) * scale_u
            uv.y = center_v + (uv.y - center_v) * scale_v
        count += 1
    return count


class PHA_OT_uv_scale_fix(bpy.types.Operator):
    bl_idname = "pha.uv_scale_fix"
    bl_label = "Fix UV Scale"
    bl_description = (
        "Scale each UV island of the selected objects using this material so the texture appears at its "
        "real-world size. Unlike Fix Texture Scale, this works per object, so objects of different sizes can share "
        "the material"
    )
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(self, context):
        if not hasattr(context, "material"):
            return False

        self.asset_id = is_ph_asset(context, context.material)
        return bool(self.asset_id)

    def execute(self, context):
        material = context.material
        slug = is_ph_asset(context, material)
        size_mm = box_mapping.get_real_size_mm(context, slug, material)
        if size_mm is None:
            self.report({"ERROR"}, f"Could not get the real-world size of {slug}")
            return {"CANCELLED"}
        size_m = (size_mm[0] / 1000, size_mm[1] / 1000)

        # Force object mode, so the mesh data is up to date and can be written to
        obj_mode = context.active_object.mode if context.active_object else "OBJECT"
        if obj_mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        users = list(tex_users(context))
        objects = [obj for obj in users if obj.select_get()]
        if not objects:
            if obj_mode != "OBJECT":
                bpy.ops.object.mode_set(mode=obj_mode)
            self.report({"ERROR"}, f"No selected objects use {material.name}")
            return {"CANCELLED"}
        done_meshes = {}
        island_count = 0
        for obj in objects:
            mesh = obj.data
            if mesh.library:
                self.report({"WARNING"}, f"{obj.name} uses linked mesh data, skipped")
                continue
            if mesh in done_meshes:
                # Instances share UVs, so they can only be correct for one scale
                if done_meshes[mesh].matrix_world.to_scale() != obj.matrix_world.to_scale():
                    self.report(
                        {"WARNING"},
                        f"{obj.name} shares its mesh with {done_meshes[mesh].name} at a different scale, "
                        f"UVs were fitted to {done_meshes[mesh].name}",
                    )
                continue
            done_meshes[mesh] = obj

            uv = next((layer for layer in mesh.uv_layers if layer.active_render), mesh.uv_layers.active)
            if uv is None:
                self.report({"WARNING"}, f"{obj.name} has no UV map, please unwrap the object first")
                continue

            slots = {i for i, slot in enumerate(obj.material_slots) if slot.material == material}
            bm = bmesh.new()
            bm.from_mesh(mesh)
            uv_layer = bm.loops.layers.uv[uv.name]
            faces = [f for f in bm.faces if f.material_index in slots]
            island_count += scale_islands(bm, faces, uv_layer, obj.matrix_world, size_m)
            bm.to_mesh(mesh)
            bm.free()
            mesh.update()

            # Fix Texture Scale stores its scale in the displacement texture too
            for mod in obj.modifiers:
                if mod.type == "DISPLACE" and mod.texture and getattr(mod.texture, "image", None):
                    if is_ph_asset(context, mod.texture.image):
                        mod.texture.crop_max_x = 1
                        mod.texture.crop_max_y = 1

        # The UVs now carry the real-world scale, so the material must not scale them again
        scale_reset = False
        for node in material.node_tree.nodes:
            if node.type == "MAPPING" and tuple(node.inputs["Scale"].default_value) != (1, 1, 1):
                node.inputs["Scale"].default_value = (1, 1, 1)
                scale_reset = True
        unselected = len([obj for obj in users if obj.data not in done_meshes])  # Instances of fixed meshes are fine
        if scale_reset and unselected:
            self.report(
                {"WARNING"},
                f"Reset the texture scale of {material.name}, which also changes the {unselected} unselected "
                f"object{'s' if unselected != 1 else ''} using it. Select and fix {'them' if unselected != 1 else 'it'} "
                "too",
            )

        if obj_mode != "OBJECT":
            bpy.ops.object.mode_set(mode=obj_mode)

        if material.pha_mapping != "UV":
            self.report({"WARNING"}, "This material uses box mapping, switch Mapping to UV to see the UV scale")
        else:
            self.report(
                {"INFO"},
                f"Scaled {island_count} UV islands on {len(done_meshes)} meshes to "
                f"{box_mapping.format_size(size_mm)}",
            )
        return {"FINISHED"}
