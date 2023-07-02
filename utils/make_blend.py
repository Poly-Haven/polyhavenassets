import bpy
import sys
from pathlib import Path

TYPES = {
    "0": "HDRIs",
    "1": "Textures",
    "2": "Models",
}


def get_catalog_id(asset_type: str, categories):
    catalog_file = Path(__file__).parents[1] / "blender_assets.cats.txt"
    lines = catalog_file.read_text().splitlines()
    lines.reverse()  # Sort by most specific to least specific
    last_cat = None
    for line in lines:
        line = line.strip()
        if not line:
            continue  # Empty lines
        if line.startswith("#"):
            continue
        if line.startswith("VERSION"):
            continue

        parts = line.split(":")
        uuid, path = parts[:2]
        crumbs = path.split("/")

        cat_type = crumbs[0]  # Either HDRIs, Textures or Models
        if TYPES[asset_type] != cat_type:
            continue
        last_cat = uuid  # In case the asset is not in any categories, revert to top level type catalog

        if len(crumbs) == 1:
            # Ignore top level type catalog from here on
            continue

        # Match catalog only if asset has all categories in its tree
        match = True
        for cat in crumbs[1:]:
            if cat.lower() not in categories:
                match = False

        if not match:
            continue

        return uuid

    return last_cat


argv = sys.argv
argv = argv[argv.index("--") + 1 :]  # get all args after "--"
slug, asset_type, thumbnail_file, authors, categories, tags, dimensions, hdr_file = argv

# Mark asset
asset = None
if asset_type == "0":  # HDRI
    asset = bpy.context.scene.world
    asset.name = slug
    group = bpy.data.node_groups["PH_HDRI_TEMPLATE"]
    group.name = slug
    img = bpy.data.images.load(hdr_file, check_existing=True)
    for n in group.nodes:
        if n.type == "TEX_ENVIRONMENT":
            n.image = img
elif asset_type == "1":  # Texture
    try:
        asset = bpy.data.materials[slug]
    except KeyError as e:
        if len(bpy.data.materials) == 1:
            asset = bpy.data.materials[0]
            asset.name = slug
        else:
            raise e
    if dimensions != "NONE":
        asset["Real Scale (mm)"] = list(float(x) for x in dimensions.split(";"))
elif asset_type == "2":  # Model
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
cat_id = get_catalog_id(asset_type, categories.split(";"))
if cat_id:
    asset.asset_data.catalog_id = cat_id
# Since an asset can only be in a single catalog, set each category as a tag too.
for c in categories.split(";"):
    asset.asset_data.tags.new(c, skip_if_exists=True)

# Set tags
for t in tags.split(";"):
    asset.asset_data.tags.new(t, skip_if_exists=True)

# Set author, description
asset.asset_data.author = authors
asset.asset_data.description = f"A CC0 {TYPES[asset_type][:-1]} by polyhaven.com"

# Make all images relative
if asset_type == "0":
    out_file = Path(hdr_file).parent / f"{slug}.blend"
else:
    out_file = Path(bpy.data.filepath)
for img in bpy.data.images:
    if not img.filepath:
        continue
    try:
        rel = Path(bpy.path.abspath(img.filepath)).resolve().relative_to(out_file.parent)
        img.filepath = f"//{rel.as_posix()}"
    except ValueError:
        print(f"WARN: Could not make {img.name} relative to {out_file.parent}")

# Save file
bpy.context.preferences.filepaths.save_version = 0  # Avoid .blend1
bpy.ops.wm.save_mainfile(filepath=str(out_file), compress=True, relative_remap=False)
