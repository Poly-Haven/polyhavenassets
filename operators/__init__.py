if "bpy" not in locals():
    from . import pull_from_polyhaven
    from . import tex_scale_fix
    from . import tex_displacement_setup
    from . import resolution_switch
    from . import cancel_download
    from . import go_to_asset
    from . import allyourbase
    from . import lod_switch
else:
    import importlib

    importlib.reload(pull_from_polyhaven)
    importlib.reload(tex_scale_fix)
    importlib.reload(tex_displacement_setup)
    importlib.reload(resolution_switch)
    importlib.reload(cancel_download)
    importlib.reload(go_to_asset)
    importlib.reload(allyourbase)
    importlib.reload(lod_switch)

import bpy  # noqa: F401

classes = [
    pull_from_polyhaven.PHA_OT_pull_from_polyhaven,
    tex_scale_fix.PHA_OT_tex_scale_fix,
    tex_displacement_setup.PHA_OT_tex_displacement_setup,
    resolution_switch.PHA_OT_resolution_switch,
    cancel_download.PHA_OT_cancel_download,
    go_to_asset.PHA_OT_go_to_asset,
    allyourbase.PHA_OT_allyourbase,
    lod_switch.PHA_OT_lod_switch,
]
