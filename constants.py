import bpy
import os
import requests

# Base URL for api.polyhaven.com. Overridable so the news feature can be tested
# against a local api before release (other legacy endpoints remain hardcoded).
API_URL = "https://api.polyhaven.com"
DATA_DIR = os.path.join(
    os.path.abspath(os.path.join(bpy.utils.resource_path("USER"), "..")),
    "data",
    "polyhaven",
)
REQ_HEADERS = requests.utils.default_headers()
REQ_HEADERS.update({"User-Agent": "Blender: PH Assets"})
