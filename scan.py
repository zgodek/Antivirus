from pathlib import Path
from index import create_index
from file import File
from database import PathError, Database
import time


class IndexDoesntExistError(Exception):
    def __init__(self, message):
        super().__init__(message)


def full_scan(path, database_fs, dict_of_files=None):
    if dict_of_files is None:
        try:
            dict_of_files = database_fs.read_index_database(path)
        except PathError:
            dict_of_files = create_index(path, database_fs)
    path = Path(path)
    files_with_viruses = []
    for item_path in path.iterdir():
        if item_path == Path(database_fs.get_path("virus_sequences_path")) \
                        or item_path == Path(database_fs.get_path("virus_hashes_path")):
            continue
        if item_path.is_dir():
            viruses_in_folder = full_scan(item_path, database_fs, dict_of_files)[0]
            files_with_viruses.extend(viruses_in_folder)
        else:
            file = File(item_path)
            item_path = item_path.as_posix()
            if check_file(item_path, database_fs):
                files_with_viruses.append(item_path)
            try:
                dict_of_files[item_path]["status"] = "Clean"
                dict_of_files[item_path]["last_scanned"] = time.time()
            except (KeyError, TypeError) as e:
                dict_of_files[item_path] = {
                    "status": "Clean",
                    "hash_md5": str(file.hash_md5()),
                    "hash_sh1": str(file.hash_sh1()),
                    "last_scanned": time.time()
                }
    return (files_with_viruses, dict_of_files)


def quick_scan(path, database_qs, dict_of_files=None):
    if dict_of_files is None:
        try:
            dict_of_files = database_qs.read_index_database(path)
        except PathError:
            error_msg = "A quick scan cannot be performed without" \
                        + "an existing index for this path, please create an index first"
            raise IndexDoesntExistError(error_msg)
    path = Path(path)
    files_with_viruses = []
    for item_path in path.iterdir():
        if item_path == Path(database_qs.get_path("virus_sequences_path")) or item_path == Path(database_qs.get_path("virus_hashes_path")):
            continue
        if item_path.is_dir():
            viruses_in_folder = quick_scan(item_path, database_qs, dict_of_files)[0]
            if viruses_in_folder != []:
                files_with_viruses.extend(viruses_in_folder)
        else:
            file = File(item_path)
            item_path = item_path.as_posix()
            try:
                if file.hash_sh1() != dict_of_files[item_path]["hash_sh1"]:
                    if check_file(item_path, database_qs):
                        files_with_viruses.append(item_path)
            except (TypeError, KeyError) as e:
                if check_file(item_path, database_qs):
                    files_with_viruses.append(item_path)
                dict_of_files[item_path] = {
                    "status": "Clean",
                    "hash_md5": str(file.hash_md5()),
                    "hash_sh1": str(file.hash_sh1()),
                    "last_scanned": time.time()
                }
    return (files_with_viruses, dict_of_files)


def check_file(path, database_chf):
    infected = False
    file = File(path)
    virus_hashes_md5 = database_chf.read_virus_database_md5()
    virus_sequences = database_chf.virus_sequences_database()
    for virus_hash_md5 in virus_hashes_md5:
        if virus_hash_md5 == file.hash_md5():
            infected = True
            remove_file(path)
    with open(file.path(), 'rb') as file_handle:
        byte_sequence = file_handle.read()
        for virus_sequence in virus_sequences:
            position = byte_sequence.find(virus_sequence)
            if position >= 0:
                infected = True
                fix_file(file.path(), virus_sequence)
    return infected


def remove_file(path):
    pass
    # os.remove(path)


def fix_file(path, virus_sequence: bytes):
    with open(path, 'rb') as file_handle:
        file_code = file_handle.read()
        file_code = file_code.replace(virus_sequence, b"")
    with open(path, 'wb') as file_handle:
        file_handle.write(file_code)
