import bpy
import logging
from pathlib import Path
from ..utils.is_ph_asset import is_ph_asset
from ..utils.get_asset_info import get_asset_info
from ..utils.get_asset_lib import get_asset_lib
from ..utils.filesize import filesize

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

    asset_lib_path = Path(get_asset_lib(context).path)

    for res in sorted_resolutions:
        local = True
        if type(asset) == bpy.types.World:
            size = files[res]["hdr"]["size"]
            if not (asset_lib_path / asset_id / f"{asset_id}_{res}.hdr").exists():
                local = False
        else:
            size = files[res]["blend"]["size"]
            for sub_path, file_info in files[res]["blend"]["include"].items():
                size += file_info["size"]
                if local:
                    if not (asset_lib_path / asset_id / sub_path).exists():
                        local = False

        op = self.layout.operator(
            "pha.resolution_switch", text=f"{res.upper()}  ({filesize(size)})", icon="CHECKMARK" if local else "IMPORT"
        )
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
