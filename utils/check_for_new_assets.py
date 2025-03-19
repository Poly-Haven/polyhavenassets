from .get_asset_lib import get_asset_lib
from .get_asset_list import get_asset_list
from ..utils.abspath import abspath


def check_for_new_assets(context, force=False):
    asset_lib = get_asset_lib(context)
    if asset_lib is None:
        return
    if not abspath(asset_lib.path).exists():
        return

    error, assets = get_asset_list("all", force)
    if error:
        return

    context.window_manager.pha_props.new_assets = 0
    for slug in assets:
        info_fp = abspath(asset_lib.path) / slug / "info.json"
        if not info_fp.exists():
            context.window_manager.pha_props.new_assets += 1
