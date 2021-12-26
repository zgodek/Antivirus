import hashlib
from pathlib import Path
import json


methods = []


class File:
    def __init__(self, path):
        self._path = path
        self._hash = hash_a_file(self.path())

    def path(self):
        return self._path

    def status(self):
        return check_file(self.path())

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
    path = Path(path)
    for item_path in path.iterdir():
        if item_path.is_dir():
            for file in create_an_index(item_path):
                index.append(file)
        elif item_path.is_file():
            index.append(File(item_path))
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


def check_file(path):
    with open(path, 'r') as file_handle:
        viruses = {}
        for line in file_handle:
            for method in methods:
                if method in line:
                    viruses[method] = line
        if viruses != {}:
            return viruses
        return False


def full_scan(path):
    path = Path(path)
    for item_path in path.iterdir():
        if item_path.is_dir():
            full_scan(item_path)
        if item_path.is_file():
            if check_file(item_path) != False:
                print(f"File {item_path} has a virus!")
                remove_viruses(item_path, check_file(item_path))
