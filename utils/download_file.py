import bpy
import logging
import requests
import threading
from pathlib import Path
from random import random
from time import sleep
from .filehash import filehash
from ..constants import REQ_HEADERS
from .. import __package__ as base_package

log = logging.getLogger(__name__)

RES = {}


def get(url, key):
    global RES
    verify_ssl = not bpy.context.preferences.addons[base_package].preferences.disable_ssl_verify
    try:
        RES[key] = requests.get(url, headers=REQ_HEADERS, verify=verify_ssl)
    except Exception as e:
        log.error(e)
        RES[key] = e


def download_file(url, dest, hash=None, retries=3):
    key = url + str(random() * 1000000)

    if hash and dest.exists():
        dest_hash = filehash(dest)
        if dest_hash.lower() == hash.lower():
            log.info(f"Skipping {Path(url).name}, already downloaded")
            return None

    log.info(f"Downloading {Path(url).name}")

    th = threading.Thread(target=get, kwargs={"url": url, "key": key})
    th.start()

    while th.is_alive() and not bpy.context.window_manager.pha_props.progress_cancel:
        sleep(0.1)

    if bpy.context.window_manager.pha_props.progress_cancel:
        msg = f"Cancelled {dest.name} mid-download"
        log.error(msg)
        return msg

    th.join()

    res = RES.pop(key)
    if isinstance(res, Exception):
        msg = f"[{type(res).__name__}] Error retrieving {url}"
        log.error(msg)
        return msg
    if res.status_code != 200:
        msg = f"Error retrieving {url}, status code: {res.status_code}"
        log.error(msg)
        return msg

    dest.parent.mkdir(parents=True, exist_ok=True)

    with dest.open("wb") as f:
        f.write(res.content)

    # Check hash again in case of incomplete download
    if hash and dest.exists():
        dest_hash = filehash(dest)
        if dest_hash.lower() != hash.lower():
            if retries > 0:
                log.warn(f"Error downloading {url}, hash mismatch. Retrying ({3 - retries + 1}/3)")
                # Wait 5s before retrying
                sleep(5)
                return download_file(url, dest, hash, retries=retries - 1)
            else:
                msg = f"Error downloading {url}, hash mismatch."
                log.error(msg)
                return msg

    return None
