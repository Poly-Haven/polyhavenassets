import bpy
import logging
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from time import sleep
from ..utils.download_file import download_file
from ..utils.get_asset_info import get_asset_info
from ..utils.get_asset_lib import get_asset_lib
from ..utils import progress

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
            if node.image is None:
                continue
            if not node.image.filepath:
                continue
            yield node.image
        if hasattr(node, "node_tree"):
            yield from get_images_in_tree(node.node_tree)


def update_image(img, asset_id, res, lib_path, info, dry_run=False):
    """
    Update image with new resolution.
    If dry_run is True, return a boolean indicating whether the image exists.
    """
    rel_path = Path(bpy.path.abspath(img.filepath)).resolve().relative_to(lib_path / asset_id).as_posix()
    new_path, file_info = get_matching_resolutions(info, res, rel_path)
    new_path = lib_path / asset_id / new_path
    if not new_path.exists():
        if dry_run:
            return False
        download_file(file_info["url"], new_path)
    if dry_run:
        return True
    img.filepath = str(new_path)
    return new_path.name


class PHA_OT_resolution_switch(bpy.types.Operator):
    bl_idname = "pha.resolution_switch"
    bl_label = "Swap texture resolution"
    bl_description = "Choose between the available texture resolutions for this asset and download its files if needed"
    bl_options = {"REGISTER", "UNDO"}

    res: bpy.props.StringProperty()
    asset_id: bpy.props.StringProperty()

    prog = 0
    prog_text = None
    num_downloaded = 0
    _timer = None
    th = None

    @classmethod
    def poll(self, context):
        return context.window_manager.pha_props.progress_total == 0

    def modal(self, context, event):
        if event.type == "TIMER":
            progress.update(context, self.prog, self.prog_text)

            if not self.th.is_alive():
                log.debug("FINISHED ALL THREADS")
                progress.end(context)
                self.th.join()
                return {"FINISHED"}

        return {"PASS_THROUGH"}

    def execute(self, context):
        import threading

        def long_task(self, images, lib_path):
            executor = ThreadPoolExecutor(max_workers=20)
            progress.init(context, len(images), word="Downloading")
            threads = []

            for img in images:
                t = executor.submit(update_image, img, self.asset_id, self.res, lib_path, info)
                threads.append(t)

            finished_threads = []
            while True:
                for tt in threads:
                    if tt._state == "FINISHED":
                        if tt not in finished_threads:
                            finished_threads.append(tt)
                            self.prog += 1
                            if tt.result() is not None:
                                self.num_downloaded += 1
                                self.prog_text = f"Downloaded {tt.result()}"
                if all(t._state == "FINISHED" for t in threads):
                    break
                sleep(0.5)

        asset_lib = get_asset_lib(context)
        if asset_lib is None:
            self.report(
                {"ERROR"},
                'First open Preferences > File Paths and create an asset library named "Poly Haven"',
            )
            return {"CANCELLED"}
        if not Path(asset_lib.path).exists():
            self.report(
                {"ERROR"},
                "Asset library path not found! Please check the folder still exists",
            )
            return {"CANCELLED"}

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
            if datablock.instance_collection:
                for obj in datablock.instance_collection.all_objects:
                    for mat in obj.material_slots:
                        trees.append(mat.material.node_tree)
                        mat.material["res"] = self.res
            else:
                # "Made real" asset, changing resolution from material settings
                datablock = context.material
                trees.append(datablock.node_tree)
        datablock["res"] = self.res

        images = []
        lib_path = Path(asset_lib.path)
        for tree in trees:
            images += get_images_in_tree(tree)
        images = list(set(images))

        images_exist = []
        for img in images:
            images_exist.append(update_image(img, self.asset_id, self.res, lib_path, info, dry_run=True))

        if all(images_exist):
            for img in images:
                update_image(img, self.asset_id, self.res, lib_path, info, dry_run=False)
            return {"FINISHED"}
        else:
            self.th = threading.Thread(target=long_task, args=(self, images, lib_path))
            self.th.start()

            wm = context.window_manager
            self._timer = wm.event_timer_add(0.1, window=context.window)
            wm.modal_handler_add(self)
            return {"RUNNING_MODAL"}
