import hashlib


class File:
    def __init__(self, path):
        self._path = path
        self._status = False

    def path(self):
        return self._path

    def set_status(self, status):
        self._status = status

    def status(self):
        return self._status

    def hash_md5(self):
        path = self._path
        BLOCKSIZE = 65536
        hasher = hashlib.sha1()
        with open(path, 'rb') as file_handle:
            buf = file_handle.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = file_handle.read(BLOCKSIZE)
        return hasher.hexdigest()

    def hash_sh1(self):
        path = self._path
        BLOCKSIZE = 65536
        hasher = hashlib.md5()
        with open(path, 'rb') as file_handle:
            buf = file_handle.read(BLOCKSIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = file_handle.read(BLOCKSIZE)
        return hasher.hexdigest()
