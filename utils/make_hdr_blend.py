import bpy
import sys
from pathlib import Path

argv = sys.argv
argv = argv[argv.index("--") + 1:]  # get all args after "--"
hdr_file, slug, thumbnail_file = argv

asset = bpy.context.scene.world
asset.asset_mark()
asset.name = slug

group = bpy.data.node_groups['PH_HDRI_TEMPLATE']
group.name = slug
img = bpy.data.images.load(hdr_file, check_existing=True)
for n in group.nodes:
    if n.type == 'TEX_ENVIRONMENT':
        n.image = img

# Set thumbnail
override = bpy.context.copy()
override["id"] = asset
with bpy.context.temp_override(**override):
    bpy.ops.ed.lib_id_load_custom_preview(filepath=thumbnail_file)


# Set catalogs

# Set tags, author, description

# Save file
bpy.context.preferences.filepaths.save_version = 0  # Avoid .blend1
out_file = Path(hdr_file).parent / f"{slug}.blend"
bpy.ops.wm.save_as_mainfile(
    filepath=str(out_file),
    compress=True,
)
