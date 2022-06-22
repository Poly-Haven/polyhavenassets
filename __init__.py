if "bpy" not in locals():
    from . import ui
    from . import operators
    from . import icons
else:
    import imp
    imp.reload(ui)
    imp.reload(operators)
    imp.reload(icons)

import bpy
from bpy.app.handlers import persistent

bl_info = {
    "name": "Poly Haven Assets",
    "description": "Dynamically adds all HDRIs, materials and 3D models from polyhaven.com into the Asset Browser",
    "author": "Poly Haven: Greg Zaal",
    "version": (0, 0, 1),
    "blender": (3, 2, 0),
    "location": "Asset Browser",
    "warning": "",
    "wiki_url": "https://github.com/Poly-Haven/polyhaven-assets",
    "tracker_url": "https://github.com/Poly-Haven/polyhaven-assets/issues",
    "category": "Import-Export",
}

classes = ui.classes + operators.classes


def register():
    icons.previews_register()

    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    icons.previews_unregister()

    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)


if __name__ == "__main__":
    register()
