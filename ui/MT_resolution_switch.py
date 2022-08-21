import bpy
import logging
from ..utils.is_ph_asset import is_ph_asset
from ..utils.get_asset_info import get_asset_info

log = logging.getLogger(__name__)

_bl_label = "Resolution"
_bl_description = "Choose between the available texture resolutions for this asset and download its files if needed"


def _draw(self, context, asset):
    asset_id = is_ph_asset(context, asset)
    if type(asset) == bpy.types.World:
        files = get_asset_info(context, asset_id)["files"]["hdri"]
    else:
        files = get_asset_info(context, asset_id)["files"]["blend"]
    sorted_resolutions = sorted(files.keys(), key=lambda x: int(x[:-1]))
    for res in sorted_resolutions:
        op = self.layout.operator("pha.resolution_switch", text=res.upper())
        op.res = res
        op.asset_id = asset_id


class PHA_MT_resolution_switch_hdri(bpy.types.Menu):
    bl_label = _bl_label
    bl_description = _bl_description

    def draw(self, context):
        _draw(self, context, context.world)


class PHA_MT_resolution_switch_texture(bpy.types.Menu):
    bl_label = _bl_label
    bl_description = _bl_description

    def draw(self, context):
        _draw(self, context, context.material)


class PHA_MT_resolution_switch_model(bpy.types.Menu):
    bl_label = _bl_label
    bl_description = _bl_description

    def draw(self, context):
        _draw(self, context, context.object.instance_collection)
