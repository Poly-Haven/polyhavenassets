import bpy
import json
import logging
from pathlib import Path

log = logging.getLogger(__name__)


class PHA_OT_allyourbase(bpy.types.Operator):
    bl_idname = "pha.allyourbasearebelongtous"
    bl_label = "(╯°□°)╯︵ ┻━┻"
    bl_description = "(╯°□°)╯︵ ┻━┻"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        data = {"early_access": True}
        fp = Path(__file__).parents[1] / "early_access.json"
        with fp.open("w") as f:
            f.write(json.dumps(data, indent=4))

        bpy.ops.console.clear()
        print(
            "\n\n     __        ___      ___     __   __   __   ___          __  ___             ___  ___  __  \n    / "
            " ` |__| |__   /\\   |     /  ` /  \\ |  \\ |__      /\\  /  `  |  | \\  /  /\\   |  |__  |  \\ \n    \\__,"
            " |  | |___ /~~\\  |     \\__, \\__/ |__/ |___    /~~\\ \\__,  |  |  \\/  /~~\\  |  |___ |__/ \n\n     __  "
            " ___  __  ___       __  ___     __        ___       __   ___  __  \n    |__) |__  /__`  |   /\\  |__)  |  "
            "   |__) |    |__  |\\ | |  \\ |__  |__) \n    |  \\ |___ .__/  |  /~~\\ |  \\  |     |__) |___ |___ | \\| "
            "|__/ |___ |  \\ \n\n\n"
        )
        if not context.screen.show_fullscreen:
            bpy.ops.screen.screen_full_area()

        return {"FINISHED"}
