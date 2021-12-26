import hashlib
from pathlib import Path
import json


class File:
    def __init__(self, path):
        self._path = path
        self._hash = hash_a_file(self.path())

    def path(self):
        return self._path

    def status(self):
        return None

    def hash(self):
        return self._hash


def hash_a_file(path):
    BLOCKSIZE = 65536
    hasher = hashlib.sha1()
    with open(path, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return hasher.hexdigest()


def create_an_index(path):
    index = []
    p = Path(path)
    for x in p.iterdir():
        if x.is_dir():
            for file in create_an_index(x):
                index.append(file)
        elif x.is_file():
            index.append(File(x))
    return index


def save_index_to_json(path):
    index = create_an_index(path.rpartition('/')[0])
    with open(path, 'w') as file_handle:
        data = []
        for file in index:
            file_data = {
                "path": str(file.path()),
                "status": str(file.status()),
                "hash": str(file.hash())
            }
            data.append(file_data)
        json.dump(data, file_handle)
