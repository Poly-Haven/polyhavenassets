import bpy
from pathlib import Path


def abspath(p):
    return Path(bpy.path.abspath(p)).resolve()
