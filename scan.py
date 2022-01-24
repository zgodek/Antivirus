from pathlib import Path
from index import create_index, PathHasToBeADirectoryError
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
    """
    goes through all of the files in the given directory and calls check_file function
    for each to search for viruses; also updates status and time of the last scan of each file in
    dict_of_files, which is read from the index for this directory, if an index for the scanned folder
    doesn't exist it creates a new index; returns the list of infected files with the updated dict_of_files
    """
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
    elif not os.path.isdir(path):
        raise PathHasToBeADirectoryError("A path to a directory is required.")
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
            (had_virus, removed) = check_file(item_path, virus_hashes_md5, virus_sequences)
            if had_virus and not removed:
                files_with_viruses.append(item_path)
                status = anwsers.virus
            elif had_virus:
                files_with_viruses.append(item_path)
            if item_path in dict_of_files:
                item_in_dict = dict_of_files[item_path]
            else:
                dict_of_files[item_path] = {}
                item_in_dict = dict_of_files[item_path]
            if os.path.isfile(item_path):
                item_in_dict["status"] = status
                item_in_dict["hash_md5"] = file.hash_md5()
                item_in_dict["last_scanned"] = time.time()
            else:
                dict_of_files.pop(item_path)
    return (files_with_viruses, dict_of_files)


def quick_scan(path, database_qs, dict_of_files=None):
    """
    reads a dict_of_files from an index and checks only those files which aren't in
    the dict_of_files or which hashes have changed or which weren't scanned before;
    also updates the index with the status of the file and current time;
    returns the list of infected files with the updated dict_of_files
    """
    virus_hashes_md5 = database_qs.read_virus_database_md5()
    virus_sequences = database_qs.read_virus_sequences_database()
    if not Path(path).exists():
        raise PathDoesntExistError("This path does not exist.")
    elif not os.path.isdir(path):
        raise PathHasToBeADirectoryError("A path to a directory is required.")
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
            item_path = item_path.as_posix()
            file = File(item_path)
            file_hash = file.hash_md5()
            if item_path in dict_of_files:
                item_in_dict = dict_of_files[item_path]
                if item_in_dict["hash_md5"] == file_hash and item_in_dict["status"] == anwsers.no_virus and item_in_dict["last_scanned"] is not None:
                    continue
            else:
                dict_of_files[item_path] = {}
                item_in_dict = dict_of_files[item_path]
            (had_virus, removed) = check_file(item_path, virus_hashes_md5, virus_sequences)
            status = anwsers.no_virus
            if had_virus and removed is False:
                files_with_viruses.append(item_path)
                status = anwsers.virus
            elif had_virus:
                files_with_viruses.append(item_path)
            if os.path.isfile(item_path):
                item_in_dict["status"] = status
                item_in_dict["hash_md5"] = file_hash
                item_in_dict["last_scanned"] = time.time()
            else:
                dict_of_files.pop(item_path)
    return (files_with_viruses, dict_of_files)


def check_file(path, virus_hashes_md5, virus_sequences):
    """
    calls check_file_fh for information if a file is infected and if it is asks user what to do about it
    returns information if a file was or still is infected and users decision
    """
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
                os.remove(path)
    if anwser == "Y":
        anwser = True
    elif anwser == "N":
        anwser = False
    elif anwser is not None:
        raise WrongAnwserError("Anwser can be Y or N.")
    return (infected, anwser)


def check_file_fh(file_handle, virus_hashes_md5, virus_sequences):
    """
    first checks if hash of byte sequence from the file matches any from the database,
    then checks if the binary code of the file contains virus sequence in it
    """
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


def fix_file(path, virus_sequence: bytes):
    """
    removes given virus sequence in the file code from given path
    """
    with open(path, 'rb') as file_handle:
        file_code = file_handle.read()
        file_code = file_code.replace(virus_sequence, b"")
    with open(path, 'wb') as file_handle:
        file_handle.write(file_code)
