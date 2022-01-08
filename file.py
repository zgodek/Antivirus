import hashlib


class File:
    def __init__(self, path):
        self._path = path
        self._hash_md5 = hash_a_file_md5(self.path())
        self._hash_sh1 = hash_a_file_sh1(self.path())

    def path(self):
        return self._path

    # def status(self):
    #     return check_file(self.path())

    def hash_md5(self):
        return self._hash_md5

    def hash_sh1(self):
        return self._hash_sh1


def hash_a_file_sh1(path):
    BLOCKSIZE = 65536
    hasher = hashlib.sha1()
    with open(path, 'rb') as file_handle:
        buf = file_handle.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = file_handle.read(BLOCKSIZE)
    return hasher.hexdigest()


def hash_a_file_md5(path):
    BLOCKSIZE = 65536
    hasher = hashlib.md5()
    with open(path, 'rb') as file_handle:
        buf = file_handle.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = file_handle.read(BLOCKSIZE)
    return hasher.hexdigest()
