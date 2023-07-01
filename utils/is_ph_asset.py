from ..utils.get_asset_lib import get_asset_lib
from ..utils.abspath import abspath


def is_ph_asset(context, asset):
    asset_id = ""
    fp = None
    try:
        fp = asset.library_weak_reference.filepath
        asset_id = abspath(fp).stem
    except AttributeError:
        return False

    lib = get_asset_lib(context)
    if not lib:
        return False

    if abspath(lib.path) not in abspath(fp).parents:
        # Is not in the PH asset lib
        return False

    return asset_id
