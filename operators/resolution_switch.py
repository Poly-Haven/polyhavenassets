import bpy
import json
import logging
import requests
import subprocess
from shutil import copy as copy_file
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from time import sleep
from ..constants import REQ_HEADERS
from ..utils.get_asset_lib import get_asset_lib
from ..utils import progress
from ..utils.get_asset_list import get_asset_list

log = logging.getLogger(__name__)


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
        log.debug(f"{self.res} {self.asset_id}")
        return {"FINISHED"}
