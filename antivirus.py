import hashlib
from pathlib import Path
import json



class File:
    def __init__(self, path):
        self._path = path
        self._hash_md5 = hash_a_file_md5(self.path())
        self._hash_sh1 = hash_a_file_sh1(self.path())

    def path(self):
        return self._path

    def status(self):
        return check_file(self.path())

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
    with open("/home/zgodek/pipr/antivirus/index.json", 'w') as file_handle:
        data = []
        for file in index:
            file_data = {
                "path": str(file.path()),
                "status": str(file.status()),
                "hash_md5": str(file.hash_md5()),
                "hash_sh1": str(file.hash_sh1())
            }
            data.append(file_data)
        json.dump(data, file_handle)


def remove_viruses(path, location):
    with open(path, 'wb') as file_handle:
        pass


def check_file(path):
    infected = False
    file = File(path)
    path_database = '/home/zgodek/pipr/antivirus/database_md5'
    path_database = Path(path_database)
    for item_path in path_database.iterdir():
        with open(item_path, 'r') as file_handle:
            if file.hash_md5() in file_handle:
                infected = True
    with open(path, 'rb') as file_handle:
        pass
    return infected


def full_scan(path):
    path = Path(path)
    files_with_viruses = []
    for item_path in path.iterdir():
        if item_path.is_dir():
            files_with_viruses.append(full_scan(item_path))
        if item_path.is_file():
            if check_file(item_path) == True:
                remove_viruses(item_path, check_file(item_path))
                files_with_viruses.append(item_path)
    return files_with_viruses


def quick_scan(path):
    path = Path(path)
    files_with_viruses = []
    for item_path in path.iterdir():
        if item_path.is_dir():
            files_with_viruses.append(quick_scan(item_path))
        else:
            file = File(item_path)
            with open("/home/zgodek/pipr/antivirus/index.json", 'r') as file_handle:
                data = json.load(file_handle)
                is_in_index = False
                for item in data:
                    if item["hash_sh1"] == file.hash_sh1():
                        is_in_index = True
                        break
                if is_in_index == False:
                    if check_file(item_path) == True:
                        remove_viruses(item_path, check_file(item_path))
                        files_with_viruses.append(item_path)
    return files_with_viruses
