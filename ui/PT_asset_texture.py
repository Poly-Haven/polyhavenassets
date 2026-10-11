import bpy
import logging
from ..utils.is_ph_asset import is_ph_asset
from ..icons import get_icons
from ..ui import statusbar
from ..ui import asset_info_box
from ..utils.get_asset_info import get_asset_info
from ..utils import box_mapping

log = logging.getLogger(__name__)

# Stored globally to avoid fetching data on every redraw
ASSET_INFO = {}


def _report_error(message):
    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title="Box Mapping", icon="ERROR")


# Material.pha_mapping items. The value is read from the node tree, so it can't get out of sync with it.
MAPPING_ITEMS = [
    ("UV", "UV", "Use the material's UV map", 0),
    ("OBJECT", "Object Box", "Box mapping in object space: the texture sticks to the object, ignoring its scale", 1),
    ("WORLD", "World Box", "Box mapping in world space: the texture continues seamlessly across objects", 2),
]


def get_mapping(material):
    node = box_mapping.get_mapping_node(material)
    if node is None:
        return 0
    return 2 if box_mapping.uses_world_coordinates(node) else 1


def set_mapping(material, value):
    if value == 0:
        box_mapping.remove(material)
        return

    world = value == 2
    node = box_mapping.get_mapping_node(material)
    if node is not None:
        box_mapping.set_world_coordinates(node, world)
        return

    context = bpy.context
    error = None
    slug = is_ph_asset(context, material)
    if not slug:
        error = "Not a Poly Haven material"
    else:
        size_mm = box_mapping.get_real_size_mm(context, slug, material)
        if size_mm is None:
            error = f"Could not get the real-world size of {slug}"
        else:
            error = box_mapping.apply(material, size_mm, world)

    if error:
        log.error(error)
        _report_error(error)


class PHA_PT_asset_texture:
    bl_label = " "
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"
    bl_options = {"HEADER_LAYOUT_EXPAND", "DEFAULT_CLOSED"}

    asset_id = ""

    @classmethod
    def poll(self, context):
        self.asset_id = is_ph_asset(context, context.material)
        if not self.asset_id:
            return False

        global ASSET_INFO
        if self.asset_id not in ASSET_INFO:
            log.debug(f"GETTING ASSET INFO {self.asset_id}")
            ASSET_INFO[self.asset_id] = get_asset_info(context, self.asset_id)
        return ASSET_INFO[self.asset_id]["type"] == 1

    def draw_header(self, context):
        icons = get_icons()
        row = self.layout.row()
        row.label(text=f"Asset: {self.asset_id}", icon_value=icons["polyhaven"].icon_id)
        sub = row.row(align=True)
        sub.alignment = "RIGHT"
        if context.window_manager.pha_props.progress_total != 0:
            statusbar.ui(self, context, statusbar=False)
        else:
            sub.menu(
                "PHA_MT_resolution_switch_texture",
                text=(context.material["res"] if "res" in context.material else "1k").upper(),
            )
            row.separator()  # Space at end

    def draw(self, context):
        layout = self.layout

        col = layout.column()
        row = col.row()
        row.operator("pha.tex_scale_fix", icon="CON_SIZELIMIT")
        row.operator("pha.uv_scale_fix", icon="UV")
        row = col.row()
        row.operator("pha.tex_displacement_setup", icon="MOD_DISPLACE")
        row = col.row()
        row.label(text="Mapping:")
        row.prop(context.material, "pha_mapping", expand=True)
        if context.material.pha_mapping != "UV" and box_mapping.SIZE_KEY in context.material:
            row = col.row()
            row.enabled = False
            row.label(text=f"Real size: {box_mapping.format_size(context.material[box_mapping.SIZE_KEY])}")
        asset_info_box.draw(self, context, col, self.asset_id)


class PHA_PT_asset_texture_eevee(bpy.types.Panel, PHA_PT_asset_texture):
    bl_parent_id = "EEVEE_MATERIAL_PT_context_material"


class PHA_PT_asset_texture_cycles(bpy.types.Panel, PHA_PT_asset_texture):
    bl_parent_id = "CYCLES_PT_context_material"
