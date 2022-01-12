from pathlib import Path
from file import File
from database import Database
import os


database = Database()


def full_scan(path):
    path = Path(path)
    files_with_viruses = []
    for item_path in path.iterdir():
        if item_path == Path(database.get_path("virus_sequences_path")) or item_path == Path(database.get_path("virus_hashes_path")):
            continue
        if item_path.is_dir():
            viruses_in_folder = full_scan(item_path)
            files_with_viruses.extend(viruses_in_folder)
        if item_path.is_file():
            if check_file(item_path):
                files_with_viruses.append(item_path)
    return files_with_viruses


def quick_scan(path, dict_of_hashes=None):
    if dict_of_hashes is None:
        dict_of_hashes = database.read_index_database()
    path = Path(path)
    files_with_viruses = []
    for item_path in path.iterdir():
        if item_path == Path(database.get_path("virus_sequences_path")) or item_path == Path(database.get_path("virus_hashes_path")):
            continue
        if item_path.is_dir():
            viruses_in_folder = quick_scan(item_path, dict_of_hashes)
            if viruses_in_folder != []:
                files_with_viruses.extend(viruses_in_folder)
        else:
            file = File(item_path)
            if file.hash_sh1() not in dict_of_hashes.values():
                if check_file(item_path):
                    files_with_viruses.append(item_path)
    return files_with_viruses


def check_file(path):
    infected = False
    file = File(path)
    virus_hashes_md5 = database.read_virus_database_md5()
    virus_sequences = database.virus_sequences_databse()
    for virus_hash_md5 in virus_hashes_md5:
        if virus_hash_md5 == file.hash_md5():
            remove_file(path)
            infected = True
    with open(file.path(), 'rb') as file_handle:
        byte_sequence = file_handle.read()
        for virus_sequence in virus_sequences:
            position = byte_sequence.find(virus_sequence)
            if position >= 0:
                fix_file(path, position)
                infected = True
    return infected


def remove_file(path):
    pass
    # os.remove(path)


def fix_file(path, position):
    pass
    # with open(path, 'wb') as file_handle:
    #     pass


def when_to_scan(time):
    pass
