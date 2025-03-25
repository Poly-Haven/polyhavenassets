def is_ph_asset(asset):
    if asset and "ph_asset_id" in asset:
        return asset["ph_asset_id"]
    else:
        return False
