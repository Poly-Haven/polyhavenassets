import bpy
import logging
import os
from pathlib import Path
from ..utils.download_file import download_file
from ..utils.get_asset_info import get_asset_info
from ..utils.get_asset_lib import get_asset_lib

log = logging.getLogger(__name__)


def remove_num(s):
    if s[-1] == "k":
        *parts, num = s[:-1].split("_")
        if num.isdigit():
            return "_".join(parts)
    return s


def get_matching_resolutions(info, res, relative_filepath):
    files = info["files"]["blend"][res]["blend"]["include"]
    for sub_path, incl in files.items():
        if remove_num(os.path.splitext(relative_filepath)[0]) == remove_num(os.path.splitext(sub_path)[0]):
            return sub_path, incl
    return None, None


class PHA_OT_resolution_switch(bpy.types.Operator):
    bl_idname = "pha.resolution_switch"
    bl_label = "Swap texture resolution"
    bl_description = "Choose between the available texture resolutions for this asset and download its files if needed"
    bl_options = {"REGISTER", "UNDO"}

    res: bpy.props.StringProperty()
    asset_id: bpy.props.StringProperty()

    @classmethod
    def poll(self, context):
        return context.window_manager.pha_props.progress_total == 0

    def execute(self, context):
        info = get_asset_info(context, self.asset_id)

        asset = None
        trees = []
        if info["type"] == 0:
            asset = context.world
            trees.append(asset.node_tree)
        elif info["type"] == 1:
            asset = context.material
            trees.append(asset.node_tree)
        elif info["type"] == 2:
            asset = context.object
            for mat in asset.material_slots:
                trees.append(mat.material.node_tree)

        for tree in trees:
            for node in tree.nodes:
                if hasattr(node, "image"):
                    lib_path = Path(get_asset_lib(context).path)
                    rel_path = (
                        Path(bpy.path.abspath(node.image.filepath)).relative_to(lib_path / self.asset_id).as_posix()
                    )
                    new_path, file_info = get_matching_resolutions(info, self.res, rel_path)
                    new_path = lib_path / self.asset_id / new_path
                    if not new_path.exists():
                        download_file(file_info["url"], new_path)
                    node.image.filepath = str(new_path)
        asset["res"] = self.res
        return {"FINISHED"}
