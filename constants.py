import bpy
import os
import requests

DATA_DIR = os.path.join(
    os.path.abspath(os.path.join(bpy.utils.resource_path("USER"), "..")),
    "data",
    "polyhaven",
)
REQ_HEADERS = requests.utils.default_headers()
REQ_HEADERS.update({"User-Agent": "Blender: PH Assets"})
