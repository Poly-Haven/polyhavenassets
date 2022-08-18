if "bpy" not in locals():
    from . import pull_from_polyhaven
    from . import tex_scale_fix
else:
    import importlib

    importlib.reload(pull_from_polyhaven)
    importlib.reload(tex_scale_fix)

import bpy  # noqa: F401

classes = [
    pull_from_polyhaven.PHA_OT_pull_from_polyhaven,
    tex_scale_fix.PHA_OT_tex_scale_fix,
]
