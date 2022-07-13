from pathlib import Path


def get_catalog_id(type: str, categories):
    types = {
        "0": "HDRIs",
        "1": "Textures",
        "2": "Models",
    }
    catalog_file = Path(__file__).parents[1] / "blender_assets.cats.txt"
    lines = catalog_file.read_text().splitlines()
    lines.reverse()  # Sort by most specific to least specific
    last_cat = None
    for line in lines:
        line = line.strip()
        if not line:
            continue  # Empty lines
        if line.startswith('#'):
            continue
        if line.startswith('VERSION'):
            continue

        parts = line.split(':')
        uuid, path = parts[:2]
        crumbs = path.split('/')

        cat_type = crumbs[0]  # Either HDRIs, Textures or Models
        if types[type] != cat_type:
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
