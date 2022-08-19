import bpy
import logging
from ..utils.is_ph_asset import is_ph_asset
from ..utils.get_asset_info import get_asset_info

log = logging.getLogger(__name__)


class PHA_MT_resolution_switch(bpy.types.Menu):
    bl_label = "Resolution"
    bl_description = "Choose between the available texture resolutions for this asset and download its files if needed"

    def draw(self, context):
        asset_id = is_ph_asset(context, context.material)
        files = get_asset_info(context, asset_id)["files"]["blend"]
        sorted_resolutions = sorted(files.keys(), key=lambda x: int(x[:-1]))
        for res in sorted_resolutions:
            op = self.layout.operator("pha.resolution_switch", text=res.upper())
            op.res = res
            op.asset_id = asset_id
