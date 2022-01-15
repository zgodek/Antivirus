from pathlib import Path
import json
from file import File
import os
import time


def create_a_list_of_files(path):
    list_of_files = []
    path = Path(path)
    for item_path in path.iterdir():
        if item_path.is_dir():
            for file in create_a_list_of_files(item_path):
                list_of_files.append(file)
        elif item_path.is_file():
            list_of_files.append(File(item_path))
    return list_of_files


def create_index(path, database, list_of_files=None):
    if list_of_files == None:
        list_of_files = create_a_list_of_files(path)
    index_path = database.get_path('index_path') + f'/{os.path.split(path)[1]}_index'
    with open(index_path, 'w') as file_handle:
        data = {}
        for file in list_of_files:
            file_data = {
                "status": str(file.status()),
                "hash_md5": str(file.hash_md5()),
                "hash_sh1": str(file.hash_sh1()),
                "last_updated": time.time()
            }
            data[str(file.path())] = file_data
        json.dump(data, file_handle)


def when_files_were_last_updated(path, database, dict_of_old_files=None):
    if dict_of_old_files == None:
        dict_of_old_files = database.read_index_database(path)
    for item_path in Path(path).iterdir():
        if item_path.is_file():
            item_path = item_path.as_posix()
            if item_path in dict_of_old_files.keys():
                last_time_updated = dict_of_old_files[item_path]["last_updated"]
                if time.time() - last_time_updated < 3600:
                    dict_of_old_files[item_path] = File(item_path)
            else:
                dict_of_old_files[item_path] = File(item_path)
        else:
            dict_of_old_files = when_files_were_last_updated(item_path, database, dict_of_old_files)
    return dict_of_old_files


def update_index(path, database):
    list_of_updated_files = []
    dict_of_updated_files = when_files_were_last_updated(path, database)
    for item in dict_of_updated_files:
        if os.path.isfile(Path(item)):
            list_of_updated_files.append(dict_of_updated_files[item])
    create_index(path, database, list_of_updated_files)
