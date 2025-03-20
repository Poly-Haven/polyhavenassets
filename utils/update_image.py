import os
from pathlib import Path
from ..utils.abspath import abspath
from ..utils.download_file import download_file


def remove_num(s):
    if s[-1] == "k":
        *parts, num = s[:-1].split("_")
        if num.isdigit():
            return "_".join(parts)
    return s


def get_matching_resolutions(info, res, relative_filepath):
    if info["type"] == 0:
        file_info = info["files"]["hdri"][res]["hdr"]
        return Path(file_info["url"]).name, file_info
    else:
        files = info["files"]["blend"][res]["blend"]["include"]
        for sub_path, file_info in files.items():
            if remove_num(os.path.splitext(relative_filepath)[0]) == remove_num(os.path.splitext(sub_path)[0]):
                return sub_path, file_info
    return None, None


def update_image(img, asset_id, res, lib_path, info, dry_run=False):
    """
    Update image with new resolution.
    If dry_run is True, return a boolean indicating whether the image exists.
    """
    rel_path = abspath(img.filepath).relative_to(lib_path.resolve() / asset_id).as_posix()
    new_path, file_info = get_matching_resolutions(info, res, rel_path)
    new_path = lib_path / asset_id / new_path
    if not new_path.exists():
        if dry_run:
            return False
        download_file(file_info["url"], new_path, file_info["md5"])
    if dry_run:
        return True
    img.filepath = str(new_path)
    img.name = new_path.name
    return new_path.name
