import bpy


class PHA_PT_main(bpy.types.Panel):

    bl_label = "Test"
    bl_space_type = "FILE_BROWSER"
    bl_region_type = "TOOLS"

    @classmethod
    def poll(self, context):
        return context.area.ui_type == "ASSETS"

    def draw(self, context):
        col = self.layout.column(align=True)
        col.label(text="Test!")
