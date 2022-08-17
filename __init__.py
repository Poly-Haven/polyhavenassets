bl_info = {
    "name": "Poly Haven Assets",
    "description": "Dynamically adds all HDRIs, materials and 3D models from polyhaven.com into the Asset Browser",
    "author": "Poly Haven",
    "version": (0, 0, 1),
    "blender": (3, 2, 0),
    "location": "Asset Browser",
    "warning": "",
    "wiki_url": "https://github.com/Poly-Haven/polyhaven-assets",
    "tracker_url": "https://github.com/Poly-Haven/polyhaven-assets/issues",
    "category": "Import-Export",
}


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


class PHAPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    def draw(self, context):
        ui.prefs_lib_reminder.prefs_lib_reminder(self, context)


classes = [PHAPreferences] + ui.classes + operators.classes


def register():
    icons.previews_register()

    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)

    bpy.types.USERPREF_PT_file_paths_asset_libraries.append(ui.prefs_lib_reminder.prefs_lib_reminder)
    bpy.types.ASSETBROWSER_PT_metadata.append(ui.asset_lib_support.ui)
    bpy.types.ASSETBROWSER_MT_editor_menus.append(ui.asset_lib_titlebar.ui)


def unregister():
    icons.previews_unregister()

    bpy.types.USERPREF_PT_file_paths_asset_libraries.remove(ui.prefs_lib_reminder.prefs_lib_reminder)
    bpy.types.ASSETBROWSER_PT_metadata.remove(ui.asset_lib_support.ui)
    bpy.types.ASSETBROWSER_MT_editor_menus.remove(ui.asset_lib_titlebar.ui)

    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)


if __name__ == "__main__":
    register()
