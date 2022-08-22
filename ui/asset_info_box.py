import logging
import time
from .. import icons
from ..utils.get_asset_info import get_asset_info

log = logging.getLogger(__name__)
ASSET_INFO = {}  # Stored globally to avoid fetching data on every redraw


def draw(self, context, layout, asset_id):
    global ASSET_INFO

    if asset_id not in ASSET_INFO:
        log.debug(f"GETTING ASSET INFO {asset_id}")
        ASSET_INFO[asset_id] = get_asset_info(context, asset_id)

    info = ASSET_INFO[asset_id]

    layout.separator()
    box = layout.box()
    col = box.column(align=True)
    col.label(text=f"Author{'s' if len(info['authors']) != 1 else ''}: {', '.join(info['authors'])}")
    col.label(text=f"Published: {time.strftime('%Y-%m-%d', time.gmtime(info['date_published']))}")
    if "dimensions" in info:
        col.label(text=f"Dimensions: {info['dimensions'][0]/1000:.2f} x {info['dimensions'][1]/1000:.2f}m")
    if "evs_cap" in info:
        col.label(text=f"Dynamic Range: {info['evs_cap']} EVs")
    if "whitebalance" in info:
        col.label(text=f"Whitebalance: {info['whitebalance']}K")
    if "coords" in info:
        gps = info["coords"]
        row = col.row(align=True)
        row.alignment = "LEFT"
        row.label(text=f"GPS: {gps[0]:.6f}, {gps[1]:.6f}")
        row.operator(
            "wm.url_open", text="", icon="LINKED", emboss=False
        ).url = f"https://www.openstreetmap.org/?mlat={gps[0]}&mlon={gps[1]}&zoom=14#map=13/{gps[0]}/{gps[1]}"

    row = box.row()
    i = icons.get_icons()
    row.operator(
        "wm.url_open", text="View on polyhaven.com", icon="URL"
    ).url = f"https://polyhaven.com/a/{self.asset_id}"
    row.operator(
        "wm.url_open", text="Support us!", icon_value=i["patreon"].icon_id
    ).url = "https://www.patreon.com/polyhaven/overview"
