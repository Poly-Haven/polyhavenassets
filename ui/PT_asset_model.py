import bpy
from pathlib import Path
from ..utils.get_asset_lib import get_asset_lib
from ..icons import get_icons


class PHA_PT_asset_model(bpy.types.Panel):

    bl_label = " "
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_options = {'HEADER_LAYOUT_EXPAND'}

    @classmethod
    def poll(self, context):
        fp = None
        try:
            fp = context.object.instance_collection.library_weak_reference.filepath
        except AttributeError:
            return False

        lib = get_asset_lib(context)
        if not lib:
            return False

        if Path(lib.path) not in Path(fp).parents:
            # Is not in the PH asset lib
            return False

        return True

    def draw_header(self, context):
        icons = get_icons()
        self.layout.label(text="Asset", icon_value=icons['polyhaven'].icon_id)

    def draw(self, context):
        layout = self.layout

        col = layout.column()
        col.label(text="Test!")
