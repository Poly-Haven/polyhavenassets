bl_info = {
    "name": "Poly Haven Assets",
    "description": "Dynamically adds all HDRIs, materials and 3D models from polyhaven.com into the Asset Browser",
    "author": "Poly Haven",
    "version": (0, 0, 1),
    "blender": (3, 2, 0),
    "location": "Asset Browser",
    "warning": "",
    "wiki_url": "https://github.com/Poly-Haven/polyhavenassets",
    "tracker_url": "https://github.com/Poly-Haven/polyhavenassets/issues",
    "category": "Import-Export",
}


if "bpy" not in locals():
    from . import ui
    from . import operators
    from . import icons
    from . import addon_updater_ops
else:
    import imp

    imp.reload(ui)
    imp.reload(operators)
    imp.reload(icons)
    imp.reload(addon_updater_ops)

import bpy
import threading
from bpy.app.handlers import persistent
from .utils.check_for_new_assets import check_for_new_assets


class PHAProperties(bpy.types.PropertyGroup):
    progress_total: bpy.props.FloatProperty(default=0, options={"HIDDEN"})  # noqa: F821
    progress_percent: bpy.props.IntProperty(
        default=0, min=0, max=100, step=1, subtype="PERCENTAGE", options={"HIDDEN"}  # noqa: F821
    )
    progress_word: bpy.props.StringProperty(options={"HIDDEN"})  # noqa: F821
    new_assets: bpy.props.IntProperty(default=0, options={"HIDDEN"})  # noqa: F821


@addon_updater_ops.make_annotations
class PHAPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    # Add-on Updater Prefs
    auto_check_update = bpy.props.BoolProperty(
        name="Auto-check for Update",
        description="If enabled, auto-check for updates using an interval",
        default=True,
    )

    updater_interval_months = bpy.props.IntProperty(
        name="Months", description="Number of months between checking for updates", default=0, min=0
    )
    updater_interval_days = bpy.props.IntProperty(
        name="Days",
        description="Number of days between checking for updates",
        default=1,
        min=0,
    )
    updater_interval_hours = bpy.props.IntProperty(
        name="Hours", description="Number of hours between checking for updates", default=0, min=0, max=23
    )
    updater_interval_minutes = bpy.props.IntProperty(
        name="Minutes", description="Number of minutes between checking for updates", default=0, min=0, max=59
    )
    updater_expand_prefs = bpy.props.BoolProperty(default=False)

    def draw(self, context):
        ui.prefs_lib_reminder.prefs_lib_reminder(self, context)

        addon_updater_ops.update_settings_ui(self, context)


classes = [PHAProperties, PHAPreferences] + ui.classes + operators.classes


@persistent
def handler(dummy):
    threading.Thread(target=check_for_new_assets, args=(bpy.context,)).start()


def register():
    addon_updater_ops.register(bl_info)
    icons.previews_register()

    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)

    bpy.types.USERPREF_PT_file_paths_asset_libraries.append(ui.prefs_lib_reminder.prefs_lib_reminder)
    bpy.types.ASSETBROWSER_PT_metadata.append(ui.asset_lib_support.ui)
    bpy.types.ASSETBROWSER_MT_editor_menus.append(ui.asset_lib_titlebar.ui)
    bpy.types.STATUSBAR_HT_header.prepend(ui.statusbar.ui)

    bpy.types.WindowManager.pha_props = bpy.props.PointerProperty(type=PHAProperties)
    bpy.app.handlers.load_post.append(handler)
    bpy.app.handlers.save_post.append(handler)


def unregister():
    addon_updater_ops.unregister()
    icons.previews_unregister()

    bpy.app.handlers.load_post.remove(handler)
    bpy.app.handlers.save_post.remove(handler)
    del bpy.types.WindowManager.pha_props

    bpy.types.USERPREF_PT_file_paths_asset_libraries.remove(ui.prefs_lib_reminder.prefs_lib_reminder)
    bpy.types.ASSETBROWSER_PT_metadata.remove(ui.asset_lib_support.ui)
    bpy.types.ASSETBROWSER_MT_editor_menus.remove(ui.asset_lib_titlebar.ui)
    bpy.types.STATUSBAR_HT_header.remove(ui.statusbar.ui)

    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)


if __name__ == "__main__":
    register()
