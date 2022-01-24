import hashlib


class File:
    def __init__(self, path):
        self._path = path
        self._status = "Unknown"

    def path(self):
        return self._path

    def status(self):
        return self._status

    def hash_md5(self):
        """
        hashes file contents from the saved path in self._path
        """
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
    """
    hashes a code of bytes
    """
    hasher = hashlib.md5()
    hasher.update(code_bytes)
    return hasher.hexdigest()
