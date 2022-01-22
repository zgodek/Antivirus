import hashlib


class File:
    def __init__(self, path):
        self._path = path
        self._status = "Unknown"

    def path(self):
        return self._path

    def set_status(self, status):
        self._status = status

    def status(self):
        return self._status

    def hash_md5(self):
        path = self._path
        BLOCKSIZE = 65536
        hasher = hashlib.md5()
        with open(path, 'rb') as file_handle:
            buf = file_handle.read(BLOCKSIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = file_handle.read(BLOCKSIZE)
        return hasher.hexdigest()


def hash_md5_bytes(code_bytes: bytes):
    BLOCKSIZE = 65536
    hasher = hashlib.md5()
    buf = code_bytes[0:BLOCKSIZE]
    if buf == code_bytes:
        hasher.update(code_bytes)
    else:
        while buf != "":
            hasher.update(buf)
            buf = code_bytes[BLOCKSIZE:BLOCKSIZE+BLOCKSIZE]
            BLOCKSIZE += BLOCKSIZE
    return hasher.hexdigest()
