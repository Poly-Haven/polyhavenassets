if "bpy" not in locals():
    from . import pull_from_polyhaven
    from . import tex_scale_fix
    from . import tex_displacement_setup
    from . import resolution_switch
    from . import cancel_download
    from . import allyourbase
else:
    import importlib

    importlib.reload(pull_from_polyhaven)
    importlib.reload(tex_scale_fix)
    importlib.reload(tex_displacement_setup)
    importlib.reload(resolution_switch)
    importlib.reload(cancel_download)
    importlib.reload(allyourbase)

import bpy  # noqa: F401

classes = [
    pull_from_polyhaven.PHA_OT_pull_from_polyhaven,
    tex_scale_fix.PHA_OT_tex_scale_fix,
    tex_displacement_setup.PHA_OT_tex_displacement_setup,
    resolution_switch.PHA_OT_resolution_switch,
    cancel_download.PHA_OT_cancel_download,
    allyourbase.PHA_OT_allyourbase,
]
