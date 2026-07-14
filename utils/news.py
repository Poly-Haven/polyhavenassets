import bpy
import os
import logging
import requests
from datetime import datetime, timezone
from ..constants import API_URL, REQ_HEADERS, DATA_DIR
from ..utils.early_access import early_access
from .. import __package__ as base_package

log = logging.getLogger(__name__)

NEWS_URL = f"{API_URL}/news/blender"
# Stored in the cross-version DATA_DIR so dismissals survive Blender upgrades and
# are shared with the new add-on (same path, same Firestore doc-id keys).
DISMISSED_FILE = os.path.join(DATA_DIR, "dismissed_news.txt")


def _ensure_data_dir():
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
    except OSError as e:
        log.warning(f"Could not create data dir {DATA_DIR}: {e}")


def read_dismissed():
    """Return the set of dismissed news keys. Robust against a missing or corrupt file."""
    try:
        with open(DISMISSED_FILE, "r") as f:
            return {line.strip() for line in f if line.strip()}
    except OSError:
        return set()


def dismiss(key):
    """Permanently record a dismissed news key (append-only, one key per line)."""
    if not key:
        return
    _ensure_data_dir()
    try:
        with open(DISMISSED_FILE, "a") as f:
            f.write(f"{key}\n")
    except OSError as e:
        log.warning(f"Could not record dismissed news: {e}")


def parse_version(v):
    """'4.2' / '4.2.0' -> (4, 2, 0). Returns None if empty or unparseable."""
    if not v:
        return None
    try:
        return tuple(int(p) for p in str(v).strip().split("."))
    except (ValueError, AttributeError):
        return None


def _parse_iso(s):
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except (ValueError, AttributeError, TypeError):
        return None


def _version_ok(item):
    ver = tuple(bpy.app.version)
    vmin = parse_version(item.get("version_min"))
    vmax = parse_version(item.get("version_max"))
    if vmin and ver < vmin:  # min is inclusive
        return False
    if vmax and ver >= vmax:  # max is exclusive
        return False
    return True


def _known_filters(early_access):
    """Audience filters this add-on version understands, mapped to whether the
    current user passes each one. New filter keys are added here over time."""
    return {
        "requires_early_access": early_access,
        "doesnt_have_early_access": not early_access,
    }


def _filters_pass(item, early_access):
    """Fail-closed: hide the item if it lists ANY filter this version doesn't
    recognise, so filters added in future never mis-target users on older add-ons."""
    filters = item.get("filters")
    if not filters:
        return True  # no filters -> shown to everyone
    if not isinstance(filters, list):
        return False
    known = _known_filters(early_access)
    for key in filters:
        if key not in known or not known[key]:
            return False
    return True


def fetch_news():
    """Fetch all news items from the API. Fails silently -> []."""
    verify_ssl = not bpy.context.preferences.addons[base_package].preferences.disable_ssl_verify
    try:
        res = requests.get(NEWS_URL, headers=REQ_HEADERS, timeout=10, verify=verify_ssl)
    except Exception as e:
        log.warning(f"[{type(e).__name__}] Could not fetch news from {NEWS_URL}")
        return []
    if res.status_code != 200:
        log.warning(f"News request to {NEWS_URL} returned {res.status_code}")
        return []
    try:
        return res.json()
    except ValueError:
        log.warning("Could not decode news response")
        return []


def select_news():
    """Return the single news item to show this session (or None).

    Applies the client-side gates the endpoint deliberately leaves to us
    (early-access, Blender version, dismissals, and a date-window re-check),
    then picks the oldest still-undismissed item (earliest date_start).
    """
    items = fetch_news()
    if not items:
        return None

    now = datetime.now(timezone.utc)
    dismissed = read_dismissed()

    eligible = []
    for item in items:
        if not item.get("active", True):
            continue
        if item.get("key") in dismissed:
            continue
        if not _filters_pass(item, early_access):
            continue
        ds = _parse_iso(item.get("date_start"))
        de = _parse_iso(item.get("date_end"))
        if ds and now < ds:
            continue
        if de and now > de:
            continue
        if not _version_ok(item):
            continue
        eligible.append(item)

    if not eligible:
        return None

    # Oldest-undismissed-first. All items share the server's ISO "…Z" format, so a
    # plain string sort is chronological.
    eligible.sort(key=lambda i: i.get("date_start") or "")
    return eligible[0]


def check_news():
    """Background entry point: select this session's news item into ephemeral state."""
    from .. import ephemeral

    ephemeral.news_item = select_news()
