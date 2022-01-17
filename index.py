from asyncore import write
from pathlib import Path
import json
from file import File
import os
from database import Database


def create_dict_of_files(path, dict_of_files=None):
    if dict_of_files is None:
        dict_of_files = {}
    path = Path(path)
    for item_path in path.iterdir():
        if item_path.is_dir():
            dict_of_files = create_dict_of_files(item_path, dict_of_files)
        elif item_path.is_file():
            item_path = item_path.as_posix()
            file = File(item_path)
            dict_of_files[item_path] = {
                "status": file.status(),
                "hash_md5": str(file.hash_md5()),
                "hash_sh1": str(file.hash_sh1()),
                "last_scanned": None
            }
    return dict_of_files


def write_dict_to_index(path, database, dict_of_files):
    index_path = database.get_path('index_path') \
                + f'/{os.path.split(path)[1]}_index'
    with open(index_path, 'w') as file_handle:
        json.dump(dict_of_files, file_handle)


def create_index(path, database):
    dict_of_files = create_dict_of_files(path)
    write_dict_to_index(path, database, dict_of_files)


def when_files_were_last_updated(path, database, dict_of_old_files=None):
    if dict_of_old_files is None:
        dict_of_old_files = database.read_index_database(path)
    for item_path in Path(path).iterdir():
        if item_path.is_file():
            item_path = item_path.as_posix()
            file = File(item_path)
            if item_path in dict_of_old_files.keys():
                last_time_scanned = dict_of_old_files[item_path]["last_scanned"]
                if last_time_scanned == None or (os.path.getmtime(item_path)
                                                      > last_time_scanned):
                    dict_of_old_files[item_path] = {
                        "status": file.status(),
                        "hash_md5": str(file.hash_md5()),
                        "hash_sh1": str(file.hash_sh1()),
                        "last_scanned": last_time_scanned
                    }
            else:
                dict_of_old_files[item_path] = {
                    "status": file.status(),
                    "hash_md5": str(file.hash_md5()),
                    "hash_sh1": str(file.hash_sh1()),
                    "last_scanned": None
                }
        else:
            dict_of_old_files = when_files_were_last_updated(item_path, database, dict_of_old_files)
    return dict_of_old_files


def update_index(path, database):
    dict_of_updated_files = when_files_were_last_updated(path, database)
    for item in dict_of_updated_files:
        if not os.path.isfile(Path(item)):
            dict_of_updated_files.pop(item)
    write_dict_to_index(path, database, dict_of_updated_files)
