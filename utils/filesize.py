def filesize(bytes):
    """
    Returns a human readable filesize
    """
    for x in ["bytes", "KB", "MB", "GB", "TB"]:
        if bytes < 1024.0:
            return f"{round(bytes)} {x}"
        bytes /= 1024.0
    return f"{round(bytes)} {x}"
