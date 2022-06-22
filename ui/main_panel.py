import bpy


class PHA_PT_main (bpy.types.Panel):

    bl_label = " "
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = 'scene'

    def draw(self, context):
        col = self.layout.column(align=True)
        col.label(text="Test!")
