"""Set the viewport display colour of newly added Poly Haven materials to the average colour of their diffuse texture.

A depsgraph handler notices when materials are added, and a timer then processes the new Poly Haven ones outside
the depsgraph update. Materials that were already in the file when it was opened are left alone.
"""

import bpy
import logging
import numpy
from .is_ph_asset import is_ph_asset
from .. import __package__ as base_package

log = logging.getLogger(__name__)

SAMPLE_SIZE = 32  # The texture is downscaled to SAMPLE_SIZE x SAMPLE_SIZE pixels before averaging
DONE_KEY = "pha_viewport_color"  # Custom prop on materials that have been processed

_known_materials = set()  # session_uid of every material we've seen
_material_count = 0
_initialized = False  # Whether _known_materials holds the materials that existed before we started watching


def find_base_color_image(material):
    """The image feeding the Principled BSDF's Base Color, searching a few nodes upstream"""
    if not material.node_tree:
        return None

    def search(socket, depth):
        for link in socket.links:
            node = link.from_node
            if node.type == "TEX_IMAGE":
                return node.image
            if depth < 5:
                for upstream in node.inputs:
                    image = search(upstream, depth + 1)
                    if image:
                        return image
        return None

    for node in material.node_tree.nodes:
        if node.type == "BSDF_PRINCIPLED":
            return search(node.inputs["Base Color"], 0)
    return None


def average_color(image):
    """Average linear RGB colour of an image, from a SAMPLE_SIZE x SAMPLE_SIZE downscaled copy"""
    small = image.copy()
    try:
        small.scale(SAMPLE_SIZE, SAMPLE_SIZE)
        pixels = numpy.empty(SAMPLE_SIZE * SAMPLE_SIZE * 4, dtype=numpy.float32)
        small.pixels.foreach_get(pixels)
    finally:
        bpy.data.images.remove(small)
    rgb = pixels.reshape(-1, 4)[:, :3]

    # Byte images hold their colour-space-encoded values, the viewport colour is linear
    if not image.is_float and image.colorspace_settings.name.lower().startswith("srgb"):
        rgb = numpy.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    return rgb.mean(axis=0).tolist()


def set_viewport_color(material):
    image = find_base_color_image(material)
    if image is None:
        return False
    try:
        color = average_color(image)
    except Exception as e:
        log.warning(f"Could not sample {image.name} for the viewport colour of {material.name}: {e}")
        return False
    material.diffuse_color = (*color, 1)
    return True


def _process_new_materials():
    if not _initialized:
        _reset_known_materials()
        return None
    new = [m for m in bpy.data.materials if m.session_uid not in _known_materials]
    _known_materials.update(m.session_uid for m in new)
    if not bpy.context.preferences.addons[base_package].preferences.auto_viewport_color:
        return None  # Still recorded above, so turning the option on later doesn't colour these
    for material in new:
        if material.library or DONE_KEY in material or not is_ph_asset(bpy.context, material):
            continue
        material[DONE_KEY] = True  # Mark it even if there's no texture, so it isn't retried
        if set_viewport_color(material):
            log.debug(f"Set viewport colour of {material.name} to {tuple(material.diffuse_color)}")
    return None  # Don't repeat the timer


def _reset_known_materials():
    global _material_count, _initialized
    _initialized = True
    _known_materials.clear()
    _known_materials.update(m.session_uid for m in bpy.data.materials)
    _material_count = len(bpy.data.materials)


@bpy.app.handlers.persistent
def hand_load_post(dummy):
    _reset_known_materials()


@bpy.app.handlers.persistent
def hand_depsgraph_update_post(scene, depsgraph):
    global _material_count
    count = len(bpy.data.materials)
    if count == _material_count:
        return
    _material_count = count
    if not bpy.app.timers.is_registered(_process_new_materials):
        bpy.app.timers.register(_process_new_materials, first_interval=0)


def _deferred_reset():
    _reset_known_materials()
    return None  # Don't repeat the timer


def register():
    # bpy.data isn't accessible while an add-on is being registered, so record the existing materials on the first
    # timer tick instead
    global _initialized
    _initialized = False
    bpy.app.timers.register(_deferred_reset, first_interval=0)
    bpy.app.handlers.load_post.append(hand_load_post)
    bpy.app.handlers.depsgraph_update_post.append(hand_depsgraph_update_post)


def unregister():
    bpy.app.handlers.load_post.remove(hand_load_post)
    bpy.app.handlers.depsgraph_update_post.remove(hand_depsgraph_update_post)
    for timer in (_deferred_reset, _process_new_materials):
        if bpy.app.timers.is_registered(timer):
            bpy.app.timers.unregister(timer)
