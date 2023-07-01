import json
from .get_asset_lib import get_asset_lib
from ..utils.abspath import abspath


def get_asset_info(context, slug):
    asset_lib = get_asset_lib(context)
    if asset_lib is None:
        return
    info_fp = abspath(asset_lib.path) / slug / "info.json"
    if not info_fp.exists():
        return

    with info_fp.open("r") as f:
        info = json.load(f)
    return info
