import imp

from . import main_panel
imp.reload(main_panel)
from . import prefs_lib_reminder
imp.reload(prefs_lib_reminder)

classes = [
    main_panel.PHA_PT_main
]
