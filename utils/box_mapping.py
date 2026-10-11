"""Real-world-scale box (triplanar) mapping for Poly Haven texture materials.

Vertical faces are projected along their own horizontal tangent, so walls at any angle get a 1:1 texture;
near-horizontal faces (|normal.z| > 0.666) are projected from above. The projection works either in object
space (the texture sticks to the object, ignoring its scale) or world space (the texture is fixed in the world, so
it continues seamlessly across separate objects).

Tangent-space normal maps rely on UV tangents, which don't match a box projection, so the material's Normal
Map nodes are bypassed with a group that builds the normal from the projection's own tangent/bitangent.
"""

import bpy
import logging
import requests
from ..constants import API_URL, REQ_HEADERS
from ..utils.get_asset_info import get_asset_info
from .. import __package__ as base_package

log = logging.getLogger(__name__)

MAPPING_GROUP = "PH Box Mapping"
NORMAL_GROUP = "PH Box Normal Map"
GROUP_VERSION = 3  # Bump when the group contents change, existing groups are rebuilt in place
ORIGINAL_KEY = "pha_box_original"  # Custom prop on our group nodes: name of the node they bypass
SIZE_KEY = "pha_box_size_mm"

# Scale modes of the mapping group. Shader trees only support Menu Switch from Blender 5.0, so 4.5 gets a checkbox.
USE_MENU = bpy.app.version >= (5, 0, 0)
MODE_SOCKET = "Scale Mode" if USE_MENU else "Real World Size"
MODE_REAL = "Real World Size"
MODE_FIXED = "Fixed Scale"
COORD_SOCKET = "Coordinates" if USE_MENU else "World Coordinates"
COORD_OBJECT = "Object"
COORD_WORLD = "World"

VERTICAL_THRESHOLD = 0.666

_size_cache = {}


def get_real_size_mm(context, slug, material=None):
    """Real-world (width, height) of a texture in millimetres, or None if unknown.

    Asks the Poly Haven API first, then falls back to the local info.json and the material's stored scale.
    """
    if slug in _size_cache:
        return _size_cache[slug]

    dims = None
    verify_ssl = not context.preferences.addons[base_package].preferences.disable_ssl_verify
    try:
        res = requests.get(f"{API_URL}/info/{slug}", headers=REQ_HEADERS, verify=verify_ssl, timeout=5)
        if res.status_code == 200:
            dims = res.json().get("dimensions")
        else:
            log.warning(f"Error retrieving info for {slug}, status code: {res.status_code}")
    except Exception as e:
        log.warning(f"[{type(e).__name__}] Error retrieving info for {slug}: {e}")

    if not dims:
        info = get_asset_info(context, slug)
        if info:
            dims = info.get("dimensions")
    if not dims and material is not None and "Real Scale (mm)" in material:
        dims = list(material["Real Scale (mm)"])

    if not dims or len(dims) < 2 or not dims[0] or not dims[1]:
        return None
    _size_cache[slug] = (float(dims[0]), float(dims[1]))
    return _size_cache[slug]


def _socket_value(socket):
    value = socket.default_value
    return tuple(value) if hasattr(value, "__len__") and not isinstance(value, str) else value


def _snapshot_users(group):
    """Input values and links of every node using this group, so they survive rebuilding its interface"""
    snapshots = []
    for material in bpy.data.materials:
        if not material.node_tree:
            continue
        for node in material.node_tree.nodes:
            if node.type != "GROUP" or node.node_tree != group:
                continue
            snapshots.append(
                {
                    "tree": material.node_tree,
                    "node": node.name,
                    "values": {s.name: _socket_value(s) for s in node.inputs if hasattr(s, "default_value")},
                    "in_links": [(s.name, s.links[0].from_socket) for s in node.inputs if s.is_linked],
                    "out_links": [(s.name, link.to_socket) for s in node.outputs for link in s.links],
                }
            )
    return snapshots


def _restore_users(snapshots):
    for snap in snapshots:
        tree = snap["tree"]
        node = tree.nodes[snap["node"]]
        for name, value in snap["values"].items():
            if name in node.inputs:
                try:
                    node.inputs[name].default_value = value
                except (TypeError, ValueError):
                    pass
        for name, from_socket in snap["in_links"]:
            if name in node.inputs:
                tree.links.new(from_socket, node.inputs[name])
        for name, to_socket in snap["out_links"]:
            if name in node.outputs:
                tree.links.new(node.outputs[name], to_socket)


def _new_group(name):
    """Returns (group, snapshots of its users), or (group, None) if it is already up to date"""
    group = bpy.data.node_groups.get(name)
    if group and group.get("pha_version") == GROUP_VERSION:
        return group, None
    snapshots = []
    if group:
        snapshots = _snapshot_users(group)
        group.nodes.clear()
        group.interface.clear()
    else:
        group = bpy.data.node_groups.new(name, "ShaderNodeTree")
    group["pha_version"] = GROUP_VERSION
    return group, snapshots


def _node(tree, bl_idname, location, label="", **props):
    node = tree.nodes.new(bl_idname)
    node.location = location
    node.label = label
    for k, v in props.items():
        setattr(node, k, v)
    return node


def _math(tree, operation, location, label=""):
    return _node(tree, "ShaderNodeMath", location, label, operation=operation)


def _vmath(tree, operation, location, label=""):
    return _node(tree, "ShaderNodeVectorMath", location, label, operation=operation)


def _mix_vector(tree, location, label=""):
    return _node(tree, "ShaderNodeMix", location, label, data_type="VECTOR", clamp_factor=False)


def set_real_size(node, size_mm):
    """Switch a mapping group node to real-world size mode with the given (width, height) in millimetres"""
    node.inputs[MODE_SOCKET].default_value = MODE_REAL if USE_MENU else True
    node.inputs["Real Width"].default_value = size_mm[0] / 1000
    node.inputs["Real Height"].default_value = size_mm[1] / 1000


def set_world_coordinates(node, world):
    if COORD_SOCKET not in node.inputs:
        get_mapping_group()  # Group from an older version of the add-on, upgrade it
    node.inputs[COORD_SOCKET].default_value = (COORD_WORLD if world else COORD_OBJECT) if USE_MENU else world


def uses_world_coordinates(node):
    if COORD_SOCKET not in node.inputs:
        return False  # Older versions only had object-relative mapping
    value = node.inputs[COORD_SOCKET].default_value
    return value == COORD_WORLD if USE_MENU else bool(value)


def get_mapping_node(material):
    """The PH Box Mapping node of a material, or None"""
    if not material or not material.node_tree:
        return None
    return next(
        (n for n in material.node_tree.nodes if _our_group(n) and n.node_tree.name.startswith(MAPPING_GROUP)),
        None,
    )


def get_mapping_group():
    group, snapshots = _new_group(MAPPING_GROUP)
    if snapshots is None:
        return group

    iface = group.interface
    iface.new_socket("Vector", in_out="OUTPUT", socket_type="NodeSocketVector")
    iface.new_socket("Tangent", in_out="OUTPUT", socket_type="NodeSocketVector")
    iface.new_socket("Bitangent", in_out="OUTPUT", socket_type="NodeSocketVector")
    loc = iface.new_socket("Location", in_out="INPUT", socket_type="NodeSocketVector")
    loc.subtype = "TRANSLATION"
    rot = iface.new_socket("Rotation", in_out="INPUT", socket_type="NodeSocketVector")
    rot.subtype = "EULER"
    coord_type = "NodeSocketMenu" if USE_MENU else "NodeSocketBool"
    coord = iface.new_socket(COORD_SOCKET, in_out="INPUT", socket_type=coord_type)
    coord.description = (
        "Object: the texture sticks to the object, ignoring its scale. "
        "World: the texture is fixed in the world and continues across objects"
    )
    if USE_MENU:
        mode = iface.new_socket(MODE_SOCKET, in_out="INPUT", socket_type="NodeSocketMenu")
    else:
        mode = iface.new_socket(MODE_SOCKET, in_out="INPUT", socket_type="NodeSocketBool")
        mode.default_value = True
    mode.description = "Size the texture by its real-world dimensions, or by a plain scale factor"
    for name in ("Real Width", "Real Height"):
        size = iface.new_socket(name, in_out="INPUT", socket_type="NodeSocketFloat")
        size.subtype = "DISTANCE"
        size.default_value = 1
        size.min_value = 0.001
        size.description = f"{name.split()[1]} of one texture tile in the real world"
    scale = iface.new_socket("Scale", in_out="INPUT", socket_type="NodeSocketVector")
    scale.subtype = "XYZ"
    scale.default_value = (1, 1, 1)
    scale.description = "Scale factor used in Fixed Scale mode"

    t = group
    L = t.links.new
    g_in = _node(t, "NodeGroupInput", (300, 300))

    # Effective scale: 1 / real size, or the fixed scale
    inv_w = _math(t, "DIVIDE", (-200, 700), "1 / Width")
    inv_w.inputs[0].default_value = 1
    L(g_in.outputs["Real Width"], inv_w.inputs[1])
    inv_h = _math(t, "DIVIDE", (-200, 550), "1 / Height")
    inv_h.inputs[0].default_value = 1
    L(g_in.outputs["Real Height"], inv_h.inputs[1])
    real_scale = _node(t, "ShaderNodeCombineXYZ", (0, 650), "Real Scale")
    L(inv_w.outputs[0], real_scale.inputs["X"])
    L(inv_h.outputs[0], real_scale.inputs["Y"])
    real_scale.inputs["Z"].default_value = 1
    if USE_MENU:
        scale_switch = _node(t, "GeometryNodeMenuSwitch", (200, 600), "Scale Mode", data_type="VECTOR")
        scale_switch.enum_items[0].name = MODE_REAL
        scale_switch.enum_items[1].name = MODE_FIXED
        L(g_in.outputs[MODE_SOCKET], scale_switch.inputs["Menu"])
        L(real_scale.outputs[0], scale_switch.inputs[MODE_REAL])
        L(g_in.outputs["Scale"], scale_switch.inputs[MODE_FIXED])
        mode.default_value = MODE_REAL  # Only valid once linked to the switch
        effective_scale = scale_switch.outputs["Output"]
    else:
        scale_switch = _mix_vector(t, (200, 600), "Scale Mode")
        L(g_in.outputs[MODE_SOCKET], scale_switch.inputs["Factor"])
        L(g_in.outputs["Scale"], scale_switch.inputs["A"])
        L(real_scale.outputs[0], scale_switch.inputs["B"])
        effective_scale = scale_switch.outputs["Result"]
    g_out = _node(t, "NodeGroupOutput", (2100, 0))

    # 0 = object space, 1 = world space
    if USE_MENU:
        coord_switch = _node(t, "GeometryNodeMenuSwitch", (-1400, 0), "Coordinates", data_type="FLOAT")
        coord_switch.enum_items[0].name = COORD_OBJECT
        coord_switch.enum_items[1].name = COORD_WORLD
        L(g_in.outputs[COORD_SOCKET], coord_switch.inputs["Menu"])
        coord_switch.inputs[COORD_OBJECT].default_value = 0
        coord_switch.inputs[COORD_WORLD].default_value = 1
        coord.default_value = COORD_OBJECT  # Only valid once linked to the switch
        is_world = coord_switch.outputs["Output"]
    else:
        is_world = g_in.outputs[COORD_SOCKET]

    # Position and geometric (flat) normal in the chosen space
    tex_coord = _node(t, "ShaderNodeTexCoord", (-1400, 300))
    geometry = _node(t, "ShaderNodeNewGeometry", (-1400, -200))
    position = _mix_vector(t, (-1000, 300), "Position")
    L(is_world, position.inputs["Factor"])
    L(tex_coord.outputs["Object"], position.inputs["A"])
    L(geometry.outputs["Position"], position.inputs["B"])
    normal_to_object = _node(
        t, "ShaderNodeVectorTransform", (-1200, -300), "Normal to Object",
        vector_type="NORMAL", convert_from="WORLD", convert_to="OBJECT",
    )
    L(geometry.outputs["True Normal"], normal_to_object.inputs["Vector"])
    normal_object = _vmath(t, "NORMALIZE", (-1000, -300))
    L(normal_to_object.outputs["Vector"], normal_object.inputs[0])
    normal = _mix_vector(t, (-1000, -100), "Normal")
    L(is_world, normal.inputs["Factor"])
    L(normal_object.outputs["Vector"], normal.inputs["A"])
    L(geometry.outputs["True Normal"], normal.inputs["B"])
    sep_p = _node(t, "ShaderNodeSeparateXYZ", (-600, 200))
    L(position.outputs["Result"], sep_p.inputs["Vector"])
    sep_n = _node(t, "ShaderNodeSeparateXYZ", (-800, -200))
    L(normal.outputs["Result"], sep_n.inputs["Vector"])

    # Near-horizontal faces use the top projection
    abs_z = _math(t, "ABSOLUTE", (-600, -100))
    L(sep_n.outputs["Z"], abs_z.inputs[0])
    is_top = _math(t, "GREATER_THAN", (-400, -100), "Is Top")
    L(abs_z.outputs[0], is_top.inputs[0])
    is_top.inputs[1].default_value = VERTICAL_THRESHOLD

    # Horizontal tangent of vertical faces: normalize(Z x N) = (-Ny, Nx, 0)
    neg_y = _math(t, "MULTIPLY", (-600, -300), "-Ny")
    L(sep_n.outputs["Y"], neg_y.inputs[0])
    neg_y.inputs[1].default_value = -1
    tangent = _node(t, "ShaderNodeCombineXYZ", (-400, -300), "Side Tangent")
    L(neg_y.outputs[0], tangent.inputs["X"])
    L(sep_n.outputs["X"], tangent.inputs["Y"])
    tangent_n = _vmath(t, "NORMALIZE", (-200, -300))
    L(tangent.outputs[0], tangent_n.inputs[0])

    # Side projection: U = distance along the wall, V = height
    u_side = _vmath(t, "DOT_PRODUCT", (-200, 300), "U = P . Tangent")
    L(position.outputs["Result"], u_side.inputs[0])
    L(tangent_n.outputs[0], u_side.inputs[1])
    side = _node(t, "ShaderNodeCombineXYZ", (0, 300), "Side")
    L(u_side.outputs["Value"], side.inputs["X"])
    L(sep_p.outputs["Z"], side.inputs["Y"])
    top = _node(t, "ShaderNodeCombineXYZ", (0, 100), "Top")
    L(sep_p.outputs["X"], top.inputs["X"])
    L(sep_p.outputs["Y"], top.inputs["Y"])

    coords = _mix_vector(t, (200, 200), "Projection")
    L(is_top.outputs[0], coords.inputs["Factor"])
    L(side.outputs[0], coords.inputs["A"])
    L(top.outputs[0], coords.inputs["B"])

    mapping = _node(t, "ShaderNodeMapping", (500, 200), vector_type="POINT")
    L(coords.outputs["Result"], mapping.inputs["Vector"])
    L(g_in.outputs["Location"], mapping.inputs["Location"])
    L(g_in.outputs["Rotation"], mapping.inputs["Rotation"])
    L(effective_scale, mapping.inputs["Scale"])
    L(mapping.outputs["Vector"], g_out.inputs["Vector"])

    # Texture-space gradients for normal mapping: side (tangent, Z), top (X, Y)
    t_mix = _mix_vector(t, (0, -300), "Tangent")
    L(is_top.outputs[0], t_mix.inputs["Factor"])
    L(tangent_n.outputs[0], t_mix.inputs["A"])
    t_mix.inputs["B"].default_value = (1, 0, 0)
    b_mix = _mix_vector(t, (0, -500), "Bitangent")
    L(is_top.outputs[0], b_mix.inputs["Factor"])
    b_mix.inputs["A"].default_value = (0, 0, 1)
    b_mix.inputs["B"].default_value = (0, 1, 0)

    # Apply the mapping's scale and Z rotation to them:
    #   T' = cos * sx * T - sin * sy * B,   B' = sin * sx * T + cos * sy * B
    sep_rot = _node(t, "ShaderNodeSeparateXYZ", (500, -200))
    L(g_in.outputs["Rotation"], sep_rot.inputs["Vector"])
    sep_scale = _node(t, "ShaderNodeSeparateXYZ", (500, -400))
    L(effective_scale, sep_scale.inputs["Vector"])
    cos = _math(t, "COSINE", (700, -150))
    L(sep_rot.outputs["Z"], cos.inputs[0])
    sin = _math(t, "SINE", (700, -250))
    L(sep_rot.outputs["Z"], sin.inputs[0])
    neg_sin = _math(t, "MULTIPLY", (700, -350))
    L(sin.outputs[0], neg_sin.inputs[0])
    neg_sin.inputs[1].default_value = -1

    def combine(name, y, t_factor, b_factor):
        t_scale = _math(t, "MULTIPLY", (900, y))
        L(t_factor.outputs[0], t_scale.inputs[0])
        L(sep_scale.outputs["X"], t_scale.inputs[1])
        b_scale = _math(t, "MULTIPLY", (900, y - 100))
        L(b_factor.outputs[0], b_scale.inputs[0])
        L(sep_scale.outputs["Y"], b_scale.inputs[1])
        t_part = _vmath(t, "SCALE", (1100, y))
        L(t_mix.outputs["Result"], t_part.inputs["Vector"])
        L(t_scale.outputs[0], t_part.inputs["Scale"])
        b_part = _vmath(t, "SCALE", (1100, y - 150))
        L(b_mix.outputs["Result"], b_part.inputs["Vector"])
        L(b_scale.outputs[0], b_part.inputs["Scale"])
        add = _vmath(t, "ADD", (1300, y))
        L(t_part.outputs["Vector"], add.inputs[0])
        L(b_part.outputs["Vector"], add.inputs[1])
        norm = _vmath(t, "NORMALIZE", (1300, y - 150))
        L(add.outputs["Vector"], norm.inputs[0])
        # The normal map works in world space
        to_world = _node(
            t, "ShaderNodeVectorTransform", (1500, y), vector_type="VECTOR", convert_from="OBJECT", convert_to="WORLD"
        )
        L(norm.outputs["Vector"], to_world.inputs["Vector"])
        world_norm = _vmath(t, "NORMALIZE", (1700, y))
        L(to_world.outputs["Vector"], world_norm.inputs[0])
        world = _mix_vector(t, (1900, y), name)
        L(is_world, world.inputs["Factor"])
        L(world_norm.outputs["Vector"], world.inputs["A"])
        L(norm.outputs["Vector"], world.inputs["B"])
        L(world.outputs["Result"], g_out.inputs[name])

    combine("Tangent", -200, cos, neg_sin)
    combine("Bitangent", -500, sin, cos)

    _restore_users(snapshots)
    for snap in snapshots:
        if "Real Width" not in snap["values"]:
            # Version 1 stored the real size as Scale = 1000 / size_mm
            sx, sy = snap["values"]["Scale"][:2]
            node = snap["tree"].nodes[snap["node"]]
            if sx and sy:
                set_real_size(node, (1000 / sx, 1000 / sy))
                node.inputs["Scale"].default_value = (1, 1, 1)

    return group


def get_normal_group():
    group, snapshots = _new_group(NORMAL_GROUP)
    if snapshots is None:
        return group

    iface = group.interface
    iface.new_socket("Normal", in_out="OUTPUT", socket_type="NodeSocketVector")
    strength = iface.new_socket("Strength", in_out="INPUT", socket_type="NodeSocketFloat")
    strength.default_value = 1
    strength.min_value = 0
    color = iface.new_socket("Color", in_out="INPUT", socket_type="NodeSocketColor")
    color.default_value = (0.5, 0.5, 1, 1)
    for name in ("Tangent", "Bitangent"):
        sock = iface.new_socket(name, in_out="INPUT", socket_type="NodeSocketVector")
        sock.hide_value = True

    t = group
    L = t.links.new
    g_in = _node(t, "NodeGroupInput", (-800, 0))
    g_out = _node(t, "NodeGroupOutput", (1000, 0))
    geometry = _node(t, "ShaderNodeNewGeometry", (-800, -300))

    # Tangent-space normal: color * 2 - 1
    decode = _vmath(t, "MULTIPLY_ADD", (-600, 100), "Decode")
    L(g_in.outputs["Color"], decode.inputs[0])
    decode.inputs[1].default_value = (2, 2, 2)
    decode.inputs[2].default_value = (-1, -1, -1)
    sep = _node(t, "ShaderNodeSeparateXYZ", (-400, 100))
    L(decode.outputs["Vector"], sep.inputs["Vector"])

    # T * x + B * y + N * z
    t_part = _vmath(t, "SCALE", (-200, 200))
    L(g_in.outputs["Tangent"], t_part.inputs["Vector"])
    L(sep.outputs["X"], t_part.inputs["Scale"])
    b_part = _vmath(t, "SCALE", (-200, 50))
    L(g_in.outputs["Bitangent"], b_part.inputs["Vector"])
    L(sep.outputs["Y"], b_part.inputs["Scale"])
    n_part = _vmath(t, "SCALE", (-200, -100))
    L(geometry.outputs["Normal"], n_part.inputs["Vector"])
    L(sep.outputs["Z"], n_part.inputs["Scale"])
    add_tb = _vmath(t, "ADD", (0, 150))
    L(t_part.outputs["Vector"], add_tb.inputs[0])
    L(b_part.outputs["Vector"], add_tb.inputs[1])
    add_n = _vmath(t, "ADD", (200, 50))
    L(add_tb.outputs["Vector"], add_n.inputs[0])
    L(n_part.outputs["Vector"], add_n.inputs[1])
    mapped = _vmath(t, "NORMALIZE", (400, 50))
    L(add_n.outputs["Vector"], mapped.inputs[0])

    # Strength blends from the shading normal, like the built-in Normal Map node
    blend = _mix_vector(t, (600, 0), "Strength")
    L(g_in.outputs["Strength"], blend.inputs["Factor"])
    L(geometry.outputs["Normal"], blend.inputs["A"])
    L(mapped.outputs["Vector"], blend.inputs["B"])
    result = _vmath(t, "NORMALIZE", (800, -150))
    L(blend.outputs["Result"], result.inputs[0])
    L(result.outputs["Vector"], g_out.inputs["Normal"])

    _restore_users(snapshots)
    return group


def _bypass(tree, original, replacement, output_name):
    """Move every link leaving original.outputs[output_name] to replacement.outputs[output_name]"""
    for link in list(original.outputs[output_name].links):
        tree.links.new(replacement.outputs[output_name], link.to_socket)
    replacement[ORIGINAL_KEY] = original.name
    replacement.parent = original.parent
    replacement.location = (original.location.x, original.location.y - 260)


def is_applied(material):
    if not material or not material.node_tree:
        return False
    return any(_our_group(n) for n in material.node_tree.nodes)


def _our_group(node):
    return node.type == "GROUP" and ORIGINAL_KEY in node and node.node_tree is not None


def apply(material, size_mm, world=False):
    """Insert box mapping into a Poly Haven material. Returns an error message, or None on success."""
    tree = material.node_tree
    if is_applied(material):
        remove(material)

    mapping = next((n for n in tree.nodes if n.type == "MAPPING"), None)
    if mapping is None:
        return "No Mapping node found in the material"

    box = tree.nodes.new("ShaderNodeGroup")
    box.node_tree = get_mapping_group()
    box.name = box.label = MAPPING_GROUP
    _bypass(tree, mapping, box, "Vector")
    set_real_size(box, size_mm)
    set_world_coordinates(box, world)
    material[SIZE_KEY] = list(size_mm)

    for normal_map in [n for n in tree.nodes if n.type == "NORMAL_MAP" and n.space == "TANGENT"]:
        box_normal = tree.nodes.new("ShaderNodeGroup")
        box_normal.node_tree = get_normal_group()
        box_normal.name = box_normal.label = NORMAL_GROUP
        for name in ("Strength", "Color"):
            src = normal_map.inputs[name]
            if src.is_linked:
                tree.links.new(src.links[0].from_socket, box_normal.inputs[name])
            else:
                box_normal.inputs[name].default_value = src.default_value
        tree.links.new(box.outputs["Tangent"], box_normal.inputs["Tangent"])
        tree.links.new(box.outputs["Bitangent"], box_normal.inputs["Bitangent"])
        _bypass(tree, normal_map, box_normal, "Normal")

    return None


def remove(material):
    """Restore the material's original mapping and normal map nodes"""
    tree = material.node_tree
    for node in [n for n in tree.nodes if _our_group(n)]:
        original = tree.nodes.get(node[ORIGINAL_KEY])
        if original is not None:
            for output in node.outputs:
                if output.name in original.outputs:
                    for link in list(output.links):
                        tree.links.new(original.outputs[output.name], link.to_socket)
        tree.nodes.remove(node)
    if SIZE_KEY in material:
        del material[SIZE_KEY]


def format_size(size_mm):
    def fmt(mm):
        return f"{mm / 1000:.3g} m" if mm >= 1000 else f"{mm:.4g} mm"

    return f"{fmt(size_mm[0])} × {fmt(size_mm[1])}"

