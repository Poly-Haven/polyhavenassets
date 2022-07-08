import bpy
import json
import os
import requests
from pathlib import Path
from ..utils.get_asset_lib import get_asset_lib


def get_asset_list():
    url = "https://api.polyhaven.com/assets?t=models"
    res = requests.get(url)

    if res.status_code != 200:
        return (f"Error retrieving asset list, status code: {res.status_code}", None)

    return (None, res.json())


def update_asset(slug, info, lib_dir):
    info_fp = lib_dir / slug / "info.json"
    if not info_fp.exists():
        download_asset(slug, info, lib_dir, info_fp)


def download_asset(slug, info, lib_dir, info_fp):
    url = f"https://api.polyhaven.com/files/{slug}"
    res = requests.get(url)

    if res.status_code != 200:
        return (f"Error retrieving file list for {slug}, status code: {res.status_code}", None)

    info['files'] = res.json()
    info_fp.parent.mkdir(parents=True, exist_ok=True)
    with info_fp.open('w') as f:
        f.write(json.dumps(info, indent=4))

    print("Downloading", slug)
    res = "1k"  # Download lowest resolution by default
    blend = info['files']['blend'][res]['blend']
    download_file(blend['url'], lib_dir / slug / f"{slug}.blend")
    for sub_path, incl in blend['include'].items():
        download_file(incl['url'], lib_dir / slug / sub_path)

    return (None, None)


def download_file(url, dest):
    print("Downloading", Path(url).name)

    res = requests.get(url)
    if res.status_code != 200:
        return f"Error retrieving {url}, status code: {res.status_code}"

    dest.parent.mkdir(parents=True, exist_ok=True)

    with dest.open("wb") as f:
        f.write(res.content)

    return None


class PHA_OT_pull_from_polyhaven(bpy.types.Operator):
    bl_idname = "pha.pull_from_polyhaven"
    bl_label = "Pull from Poly Haven"
    bl_description = "Updates the local asset library with new assets from polyhaven.com"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):

        asset_lib = get_asset_lib(context)
        if asset_lib is None:
            self.report({'ERROR'}, "First open Preferences > File Paths and create an asset library named \"Poly Haven\"")
            return {'CANCELLED'}
        if not Path(asset_lib.path).exists():
            self.report({'ERROR'}, "Asset library path not found! Please check the folder still exists")
            return {'CANCELLED'}

        error, assets = get_asset_list()
        if error:
            self.report({'ERROR'}, error)
            return {'CANCELLED'}

        for slug, asset in assets.items():
            update_asset(slug, asset, Path(asset_lib.path))

        self.report({'INFO'}, "Downloaded")
        return {'FINISHED'}
