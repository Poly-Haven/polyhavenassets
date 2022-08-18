from pathlib import Path
from ..utils.get_asset_lib import get_asset_lib


def is_ph_asset(context, asset):
    asset_id = ""
    fp = None
    try:
        fp = asset.library_weak_reference.filepath
        asset_id = Path(fp).stem
    except AttributeError:
        return False

    lib = get_asset_lib(context)
    if not lib:
        return False

    if Path(lib.path) not in Path(fp).parents:
        # Is not in the PH asset lib
        return False

    return asset_id
