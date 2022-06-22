import bpy


def dpi_factor():
    prefs = bpy.context.preferences.system
    retinafac = bpy.context.preferences.system.pixel_size
    return prefs.dpi / (72 / retinafac)
