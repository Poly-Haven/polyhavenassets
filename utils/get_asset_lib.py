def get_asset_lib(context):
    """Get or create the Poly Haven asset library"""

    for l in context.preferences.filepaths.asset_libraries:
        if l.name.lower() == "poly haven":
            return l

    return None
