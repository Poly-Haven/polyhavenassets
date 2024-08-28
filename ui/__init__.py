try:
    import importlib

    importer = importlib
except ImportError:
    try:
        import imp

        importer = imp
    except ImportError:
        raise ModuleNotFoundError("Cannot find the imp/importlib module")

from . import prefs_lib_reminder
from . import asset_lib_support
from . import asset_lib_titlebar
from . import statusbar
from . import PT_asset_hdri
from . import PT_asset_model
from . import PT_asset_texture
from . import PT_sidebar
from . import MT_resolution_switch
from . import MT_pull_by_type
from . import MT_lod_switch

importer.reload(prefs_lib_reminder)
importer.reload(asset_lib_support)
importer.reload(asset_lib_titlebar)
importer.reload(statusbar)
importer.reload(PT_asset_hdri)
importer.reload(PT_asset_model)
importer.reload(PT_asset_texture)
importer.reload(PT_sidebar)
importer.reload(MT_resolution_switch)
importer.reload(MT_pull_by_type)
importer.reload(MT_lod_switch)

classes = [
    PT_asset_hdri.PHA_PT_asset_hdri,
    PT_asset_model.PHA_PT_asset_model,
    PT_asset_model.PHA_PT_asset_model_eevee,
    PT_asset_model.PHA_PT_asset_model_cycles,
    PT_asset_texture.PHA_PT_asset_texture_eevee,
    PT_asset_texture.PHA_PT_asset_texture_cycles,
    PT_sidebar.PHA_PT_sidebar,
    MT_resolution_switch.PHA_MT_resolution_switch_hdri,
    MT_resolution_switch.PHA_MT_resolution_switch_texture,
    MT_resolution_switch.PHA_MT_resolution_switch_model,
    MT_pull_by_type.PHA_MT_pull_by_type,
    MT_lod_switch.PHA_MT_lod_switch,
]
