from pathlib import Path, PurePath
import json
from file import File
import os


class PathHasToBeADirectoryError(Exception):
    def __init__(self, message):
        super().__init__(message)


def create_dict_of_files(path, database, dict_of_files=None):
    """
    creates a dictionary of file paths found in the given directory path; those
    file paths are keys to other dictionaries, containting status, hash and time
    of the last scan of a file to which the path leads
    """
    if dict_of_files is None:
        dict_of_files = {}
    if not os.path.isdir(path):
        raise PathHasToBeADirectoryError("A path to a directory is required.")
    path = Path(path)
    for item_path in path.iterdir():
        if item_path in database.get_paths():
            continue
        if item_path.is_dir():
            dict_of_files = create_dict_of_files(item_path, database, dict_of_files)
        elif item_path.is_file():
            item_path = item_path.as_posix()
            file = File(item_path)
            dict_of_files[item_path] = {
                "status": file.status(),
                "hash_md5": file.hash_md5(),
                "last_scanned": None
            }
    return dict_of_files


def write_dict_to_index(path, database, dict_of_files):
    """
    saves given dictionary of files to a json file in the index folder, which path
    is read from given database
    """
    path = PurePath(path)
    index_path = database.get_path('index_path') \
                + f'/{path.name}_index'
    with open(index_path, 'w') as file_handle:
        json.dump(dict_of_files, file_handle)


def create_index(path, database):
    """
    creates a new index of a given path
    """
    dict_of_files = create_dict_of_files(path, database)
    write_dict_to_index(path, database, dict_of_files)


def have_files_changed(path, database, dict_of_old_files=None):
    """
    iterates a directory and checks if a file was ever scanned and if so, it checks if this file
    was modified after being scanned
    """
    if dict_of_old_files is None:
        dict_of_old_files = database.read_index_database(path)
    for item_path in Path(path).iterdir():
        if item_path in database.get_paths():
            continue
        if item_path.is_file():
            item_path = item_path.as_posix()
            file = File(item_path)
            if item_path in dict_of_old_files.keys():
                last_time_scanned = dict_of_old_files[item_path]["last_scanned"]
                if last_time_scanned is None or (os.path.getmtime(item_path)
                                                > float(last_time_scanned)):
                    dict_of_old_files[item_path] = {
                        "status": file.status(),
                        "hash_md5": file.hash_md5(),
                        "last_scanned": last_time_scanned
                    }
            else:
                dict_of_old_files[item_path] = {
                    "status": file.status(),
                    "hash_md5": file.hash_md5(),
                    "last_scanned": None
                }
        else:
            dict_of_old_files = have_files_changed(item_path, database, dict_of_old_files)
    return dict_of_old_files


def update_index(path, database):
    """
    calls have_files_changed to have updated index of files
    checks if a file, which path is saved in the index wasn't removed
    """
    if not os.path.isdir(path):
        raise PathHasToBeADirectoryError("A path to a directory is required.")
    dict_of_updated_files = have_files_changed(path, database)
    dict_of_not_erased_files = {}
    for item in dict_of_updated_files:
        if (Path(item).is_file()):
            dict_of_not_erased_files[item] = dict_of_updated_files[item]
    write_dict_to_index(path, database, dict_of_not_erased_files)
