from pathlib import Path
from index import create_index
from file import File, hash_md5_bytes
from database import IndexError
import time
import os
import collections


Anwser = collections.namedtuple("Anwser", ['no_virus', 'virus'])
anwsers = Anwser("Clean", "Infected")


class IndexDoesntExistError(Exception):
    def __init__(self, message):
        super().__init__(message)


class PathDoesntExistError(Exception):
    def __init__(self, message):
        super().__init__(message)


class WrongAnwserError(Exception):
    def __init__(self, message):
        super().__init__(message)


def full_scan(path, database_fs, dict_of_files=None):
    virus_hashes_md5 = database_fs.read_virus_database_md5()
    virus_sequences = database_fs.read_virus_sequences_database()
    if dict_of_files is None or dict_of_files == {}:
        try:
            dict_of_files = database_fs.read_index_database(path)
        except IndexError:
            create_index(path, database_fs)
            dict_of_files = database_fs.read_index_database(path)
    if not os.path.exists(path):
        raise PathDoesntExistError("This path does not exist.")
    path = Path(path)
    files_with_viruses = []
    for item_path in path.iterdir():
        if item_path in database_fs.get_paths():
            continue
        elif item_path.is_dir():
            (viruses_in_folder, dict_of_files) = full_scan(item_path, database_fs, dict_of_files)
            if viruses_in_folder != []:
                files_with_viruses.extend(viruses_in_folder)
        else:
            status = anwsers.no_virus
            item_path = item_path.as_posix()
            file = File(item_path)
            (has_virus, is_fixed) = check_file(item_path, virus_hashes_md5, virus_sequences)
            if has_virus and not is_fixed:
                files_with_viruses.append(item_path)
                status = anwsers.virus
            elif has_virus:
                files_with_viruses.append(item_path)
            try:
                item_in_dict = dict_of_files[item_path]
                item_in_dict["last_scanned"] = time.time()
                item_in_dict["status"] = status
            except (TypeError, KeyError) as e:
                dict_of_files[item_path] = {
                    "status": status,
                    "hash_md5": file.hash_md5(),
                    "last_scanned": time.time()
                }
    return (files_with_viruses, dict_of_files)


def quick_scan(path, database_qs, dict_of_files=None):
    virus_hashes_md5 = database_qs.read_virus_database_md5()
    virus_sequences = database_qs.read_virus_sequences_database()
    if not Path(path).exists():
        raise PathDoesntExistError("This path does not exist.")
    if dict_of_files is None:
        try:
            dict_of_files = database_qs.read_index_database(path)
        except IndexError:
            error_msg = "A quick scan cannot be performed without" \
                        + " an existing index for this path, please create an index first."
            raise IndexDoesntExistError(error_msg)
    path = Path(path)
    files_with_viruses = []
    for item_path in path.iterdir():
        if item_path in database_qs.get_paths():
            continue
        elif item_path.is_dir():
            (viruses_in_folder, dict_of_files) = quick_scan(item_path, database_qs, dict_of_files)
            if viruses_in_folder != []:
                files_with_viruses.extend(viruses_in_folder)
        else:
            status = anwsers.no_virus
            item_path = item_path.as_posix()
            file = File(item_path)
            try:
                item_in_dict = dict_of_files[item_path]
                if file.hash_md5() != item_in_dict["hash_md5"] or item_in_dict["status"] == file.status():
                    (has_virus, user_decision) = check_file(item_path, virus_hashes_md5, virus_sequences)
                    if has_virus and user_decision is False:
                        files_with_viruses.append(item_path)
                        status = anwsers.virus
                    elif has_virus:
                        files_with_viruses.append(item_path)
                    item_in_dict["status"] = status
                    item_in_dict["last_scanned"] = time.time()
            except (TypeError, KeyError) as e:
                (has_virus, user_decision) = check_file(item_path, virus_hashes_md5, virus_sequences)
                if has_virus and user_decision is False:
                    files_with_viruses.append(item_path)
                    status = anwsers.virus
                elif has_virus:
                    files_with_viruses.append(item_path)
                dict_of_files[item_path] = {
                    "status": status,
                    "hash_md5": file.hash_md5(),
                    "last_scanned": time.time()
                }
    return (files_with_viruses, dict_of_files)


def check_file(path, virus_hashes_md5, virus_sequences):
    anwser = None
    infected = False
    with open(path, 'rb') as file_handle:
        (infected, found_virus_seq) = check_file_fh(file_handle, virus_hashes_md5, virus_sequences)
        if infected is True and found_virus_seq != []:
            anwser = input(f"Do you want to fix this infected file? {path} Y/N\n")
            if anwser == "Y":
                for virus_sequence in found_virus_seq:
                    fix_file(path, virus_sequence)
        elif infected is True and found_virus_seq == []:
            anwser = input(f"Do you want to remove this infected file? {path} Y/N\n")
            if anwser == "Y":
                remove_file(path)
    if anwser == "Y":
        anwser = True
    elif anwser == "N":
        anwser = False
    elif anwser is not None:
        raise WrongAnwserError("Anwser can be Y or N.")
    return (infected, anwser)


def check_file_fh(file_handle, virus_hashes_md5, virus_sequences):
    infected = False
    found_virus_seq = []
    byte_sequence = file_handle.read()
    hashed_file = hash_md5_bytes(byte_sequence)
    for virus_hash_md5 in virus_hashes_md5:
        if virus_hash_md5 == hashed_file:
            infected = True
    for virus_sequence in virus_sequences:
        position = byte_sequence.find(virus_sequence)
        if position >= 0:
            infected = True
            found_virus_seq.append(virus_sequence)
    return (infected, found_virus_seq)


def remove_file(path):
    os.remove(path)


def fix_file(path, virus_sequence: bytes):
    with open(path, 'rb') as file_handle:
        file_code = file_handle.read()
        file_code = file_code.replace(virus_sequence, b"")
    with open(path, 'wb') as file_handle:
        file_handle.write(file_code)
