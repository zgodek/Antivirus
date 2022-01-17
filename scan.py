from pathlib import Path
from unittest import result
from index import create_index
from file import File
from database import Database, PathError
import time
import os


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
        elif item_path.is_dir():
            results_of_full_scan = full_scan(item_path, database_fs, dict_of_files)
            dict_of_files = results_of_full_scan[1]
            viruses_in_folder = results_of_full_scan[0]
            if viruses_in_folder != []:
                files_with_viruses.extend(viruses_in_folder)
        elif item_path.is_file():
            status = "Clean"
            file = File(item_path)
            item_path = item_path.as_posix()
            check_file_results = check_file(item_path, database_fs)
            if check_file_results[0] is True and check_file_results[1] == "N":
                files_with_viruses.append(item_path)
                status = "Infected"
            elif check_file_results[0]:
                files_with_viruses.append(item_path)
            try:
                dict_of_files[item_path]["last_scanned"] = time.time()
                dict_of_files[item_path]["status"] = status
            except (TypeError, KeyError) as e:
                dict_of_files[item_path] = {
                    "status": status,
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
        status = "Clean"
        if item_path == Path(database_qs.get_path("virus_sequences_path")) or item_path == Path(database_qs.get_path("virus_hashes_path")):
            continue
        if item_path.is_dir():
            results_of_quick_scan = quick_scan(item_path, database_qs, dict_of_files)
            viruses_in_folder = results_of_quick_scan[0]
            dict_of_files = results_of_quick_scan[1]
            if viruses_in_folder != []:
                files_with_viruses.extend(viruses_in_folder)
        else:
            item_path = item_path.as_posix()
            file = File(item_path)
            try:
                if file.hash_sh1() != dict_of_files[item_path]["hash_sh1"] or dict_of_files[item_path]["status"] == file.status():
                    check_file_results = check_file(item_path, database_qs)
                    if check_file_results[0] is True and check_file_results[1] == "N":
                        files_with_viruses.append(item_path)
                        dict_of_files[item_path]["status"] = "Infected"
                    elif check_file_results[0]:
                        files_with_viruses.append(item_path)
                        dict_of_files[item_path]["status"] = status
                    dict_of_files[item_path]["status"] = status
                    dict_of_files[item_path]["last_scanned"] = time.time()
            except (TypeError, KeyError) as e:
                check_file_results = check_file(item_path, database_qs)
                if check_file_results[0] is True and check_file_results[1] == "N":
                        files_with_viruses.append(item_path)
                        status = "Infected"
                dict_of_files[item_path] = {
                    "status": status,
                    "hash_md5": str(file.hash_md5()),
                    "hash_sh1": str(file.hash_sh1()),
                    "last_scanned": time.time()
                }
    return (files_with_viruses, dict_of_files)


def check_file(path, database_chf):
    anwser = None
    infected = False
    file = File(path)
    virus_hashes_md5 = database_chf.read_virus_database_md5()
    virus_sequences = database_chf.virus_sequences_database()
    for virus_hash_md5 in virus_hashes_md5:
        if virus_hash_md5 == file.hash_md5():
            infected = True
            anwser = input(f"Do you want to remove this infected file? {file.path()} Y/N\n")
            if anwser == "Y":
                remove_file(path)
    with open(file.path(), 'rb') as file_handle:
        byte_sequence = file_handle.read()
        for virus_sequence in virus_sequences:
            position = byte_sequence.find(virus_sequence)
            if position >= 0:
                infected = True
                anwser = input(f"Do you want to fix this infected file? {file.path()} Y/N\n")
                if anwser == "Y":
                    fix_file(file.path(), virus_sequence)
    return (infected, anwser)


def remove_file(path):
    os.remove(path)


def fix_file(path, virus_sequence: bytes):
    with open(path, 'rb') as file_handle:
        file_code = file_handle.read()
        file_code = file_code.replace(virus_sequence, b"")
    with open(path, 'wb') as file_handle:
        file_handle.write(file_code)
