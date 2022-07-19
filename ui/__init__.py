import imp

from . import main_panel
imp.reload(main_panel)

from . import prefs_lib_reminder
imp.reload(prefs_lib_reminder)

from . import asset_lib_panel
imp.reload(asset_lib_panel)

from . import PT_asset_model
imp.reload(PT_asset_model)

classes = [
    main_panel.PHA_PT_main,
    PT_asset_model.PHA_PT_asset_model,
]
