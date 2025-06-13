import bpy
import logging
from ..utils.is_ph_asset import is_ph_asset
from ..icons import get_icons
from ..ui import statusbar
from ..ui import asset_info_box
from ..utils.get_asset_info import get_asset_info

log = logging.getLogger(__name__)

# Stored globally to avoid fetching data on every redraw
ASSET_INFO = {}


class PHA_PT_asset_model_base:
    bl_label = " "
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_parent_id = "OBJECT_PT_context_object"
    bl_options = {"HEADER_LAYOUT_EXPAND", "DEFAULT_CLOSED"}

    asset_id = ""

    @classmethod
    def poll(self, context):
        self.asset_id = is_ph_asset(context, context.object.instance_collection)
        return bool(self.asset_id)

    def has_lods(self, context):
        lod_str = context.object.instance_collection.library_weak_reference.id_name[-5:]  # _LOD0, _LOD1, etc
        if lod_str[:-1] == "_LOD":
            if lod_str[-1].isdigit():
                return True
        return False

    def draw_header(self, context):
        icons = get_icons()
        row = self.layout.row()
        row.label(text=f"Asset: {self.asset_id}", icon_value=icons["polyhaven"].icon_id)
        sub = row.row(align=True)
        sub.alignment = "RIGHT"
        if context.window_manager.pha_props.progress_total != 0:
            statusbar.ui(self, context, statusbar=False)
        else:
            if self.bl_context == "data":
                ref = context.object.instance_collection
                if self.has_lods(context):
                    sub.menu(
                        "PHA_MT_lod_switch",
                        text=ref.library_weak_reference.id_name[-4:],
                    )
                sub.menu(
                    "PHA_MT_resolution_switch_model",
                    text=(ref.get("res", context.object.get("res", "1k"))).upper(),
                )
            else:
                sub.menu(
                    "PHA_MT_resolution_switch_texture",
                    text=(context.material["res"] if "res" in context.material else "1k").upper(),
                )
            row.separator()  # Space at end

    def draw(self, context):
        layout = self.layout

        col = layout.column()
        col.operator("object.duplicates_make_real", text="Edit Asset", icon="GREASEPENCIL")
        asset_info_box.draw(self, context, col, self.asset_id)


class PHA_PT_asset_model(bpy.types.Panel, PHA_PT_asset_model_base):
    bl_label = " "


def is_model_material(context, asset_id):
    asset_id = is_ph_asset(context, context.material)
    if not asset_id:
        return False

    global ASSET_INFO
    if asset_id not in ASSET_INFO:
        log.debug(f"GETTING ASSET INFO {asset_id}")
        ASSET_INFO[asset_id] = get_asset_info(context, asset_id)
    return ASSET_INFO[asset_id]["type"] == 2


class PHA_PT_asset_model_eevee(bpy.types.Panel, PHA_PT_asset_model_base):
    bl_context = "material"
    bl_parent_id = "EEVEE_MATERIAL_PT_context_material"

    @classmethod
    def poll(self, context):
        self.asset_id = is_ph_asset(context, context.material)
        return is_model_material(context, self.asset_id)


class PHA_PT_asset_model_cycles(bpy.types.Panel, PHA_PT_asset_model_base):
    bl_context = "material"
    bl_parent_id = "CYCLES_PT_context_material"

    @classmethod
    def poll(self, context):
        self.asset_id = is_ph_asset(context, context.material)
        return is_model_material(context, self.asset_id)
