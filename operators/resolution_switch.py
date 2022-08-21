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
    if info["type"] == 0:
        file_info = info["files"]["hdri"][res]["hdr"]
        return Path(file_info["url"]).name, file_info
    else:
        files = info["files"]["blend"][res]["blend"]["include"]
        for sub_path, file_info in files.items():
            if remove_num(os.path.splitext(relative_filepath)[0]) == remove_num(os.path.splitext(sub_path)[0]):
                return sub_path, file_info
    return None, None


def get_images_in_tree(tree):
    for node in tree.nodes:
        if hasattr(node, "image"):
            yield node.image
        if hasattr(node, "node_tree"):
            yield from get_images_in_tree(node.node_tree)


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

        datablock = None
        trees = []
        if info["type"] == 0:
            datablock = context.world
            trees.append(datablock.node_tree)
        elif info["type"] == 1:
            datablock = context.material
            trees.append(datablock.node_tree)
        elif info["type"] == 2:
            datablock = context.object
            for obj in datablock.instance_collection.all_objects:
                for mat in obj.material_slots:
                    trees.append(mat.material.node_tree)

        images = []
        for tree in trees:
            images += get_images_in_tree(tree)
            for img in images:
                lib_path = Path(get_asset_lib(context).path)
                rel_path = Path(bpy.path.abspath(img.filepath)).relative_to(lib_path / self.asset_id).as_posix()
                new_path, file_info = get_matching_resolutions(info, self.res, rel_path)
                new_path = lib_path / self.asset_id / new_path
                if not new_path.exists():
                    download_file(file_info["url"], new_path)
                img.filepath = str(new_path)
        datablock["res"] = self.res
        return {"FINISHED"}
