import bpy
import sys

argv = sys.argv
argv = argv[argv.index("--") + 1:]  # get all args after "--"
slug, asset_type, thumbnail_file = argv

# Mark asset
asset = None
if asset_type == '1':  # Texture
    asset = bpy.data.materials[slug]
elif asset_type == '2':  # Model
    asset = bpy.data.collections[slug]
else:
    # Unsupported type
    sys.exit()

if asset:
    asset.asset_mark()

# Set thumbnail
override = bpy.context.copy()
override["id"] = asset
with bpy.context.temp_override(**override):
    bpy.ops.ed.lib_id_load_custom_preview(filepath=thumbnail_file)


# Set catalogs

# Set tags, author, description

# Save file
bpy.context.preferences.filepaths.save_version = 0  # Avoid .blend1
bpy.ops.wm.save_mainfile(compress=True)
