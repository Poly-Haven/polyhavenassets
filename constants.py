import bpy
import os
import requests
from . import bl_info

DATA_DIR = os.path.join(os.path.abspath(os.path.join(
    bpy.utils.resource_path('USER'), '..')), 'data', 'polyhaven')
REQ_HEADERS = requests.utils.default_headers()
REQ_HEADERS.update({
    'User-Agent': f"Blender {bpy.app.version_string}: {bl_info['name']} {'.'.join(str(i) for i in bl_info['version'])}"
})
