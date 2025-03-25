import bpy
import logging
from ..utils.get_asset_lib import get_asset_lib
from ..utils.abspath import abspath

log = logging.getLogger(__name__)


def is_our_asset(context, asset):
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


def post_import(lapp_context):
    asset = lapp_context.import_items[0].id
    asset_id = is_our_asset(bpy.context, asset)

    if not asset_id:
        # Not one of our assets
        return

    for item in lapp_context.import_items:
        item.id["ph_asset_id"] = asset_id  # Store asset ID in the datablock custom properties
