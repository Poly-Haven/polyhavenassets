from hashlib import md5


def filehash(fp):
    """Gets the hash of a file in a memory-efficient way"""
    with open(fp, "rb") as f:
        file_hash = md5()
        chunk = f.read(8192)
        while chunk:
            file_hash.update(chunk)
            chunk = f.read(8192)
        return file_hash.hexdigest()
