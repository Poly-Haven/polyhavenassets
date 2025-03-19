import bpy
import logging
import requests
import time
import threading
from ..constants import REQ_HEADERS
from .. import icons
from ..utils.get_asset_info import get_asset_info
from .. import __package__ as base_package

log = logging.getLogger(__name__)

# Stored globally to avoid fetching data on every redraw
ASSET_INFO = {}
SPONSOR_INFO = {}


def get_sponsor_info(uid):
    log.debug(f"GETTING SPONSOR INFO {uid}")
    url = f"https://api.polyhaven.com/sponsor/{uid}"
    verify_ssl = not bpy.context.preferences.addons[base_package].preferences.disable_ssl_verify
    res = requests.get(url, headers=REQ_HEADERS, verify=verify_ssl)

    if res.status_code != 200:
        log.error(f"Error retrieving sponsor info, status code: {res.status_code}")
        return None

    SPONSOR_INFO[uid] = res.json()


def draw(self, context, layout, asset_id):
    global ASSET_INFO
    i = icons.get_icons()

    if asset_id not in ASSET_INFO:
        log.debug(f"GETTING ASSET INFO {asset_id}")
        ASSET_INFO[asset_id] = get_asset_info(context, asset_id)

    info = ASSET_INFO[asset_id]

    if not info:
        return

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
        row.operator("wm.url_open", text="", icon="LINKED", emboss=False).url = (
            f"https://www.openstreetmap.org/?mlat={gps[0]}&mlon={gps[1]}&zoom=14#map=13/{gps[0]}/{gps[1]}"
        )

    col.separator()
    row = col.row(align=True)
    row.alignment = "CENTER"
    row.label(text="", icon_value=i["heart"].icon_id)
    row.label(text="Sponsored by:")
    row.operator("wm.url_open", text="", icon="QUESTION").url = "https://www.patreon.com/polyhaven/overview"
    if "sponsors" not in info or not info["sponsors"]:
        row = col.row()
        row.alignment = "CENTER"
        row.label(text="No one yet :(")
    else:
        for uid in info["sponsors"]:
            row = col.row(align=True)
            row.alignment = "CENTER"
            if not isinstance(uid, str):
                sponsor_data = uid
            else:
                if uid in SPONSOR_INFO:
                    sponsor_data = SPONSOR_INFO[uid]
                else:
                    sponsor_data = {"name": "Loading..."}
                    SPONSOR_INFO[uid] = sponsor_data
                    th = threading.Thread(target=get_sponsor_info, args=(uid,))
                    th.start()
            row.label(text=sponsor_data["name"])
            if "url" in sponsor_data:
                row.operator("wm.url_open", text="", icon="LINKED", emboss=False).url = sponsor_data["url"]

    row = box.row()
    row.operator("wm.url_open", text="View on polyhaven.com", icon="URL").url = (
        f"https://polyhaven.com/a/{self.asset_id}"
    )
    row.operator("wm.url_open", text="Support us!", icon_value=i["patreon"].icon_id).url = (
        "https://www.patreon.com/polyhaven/overview"
    )
