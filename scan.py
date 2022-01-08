from pathlib import Path
from file import File
from database import read_index_database, read_virus_database_md5, read_virus_database_sequences

virus_hashes_md5 = read_virus_database_md5("/home/zgodek/pipr/antivirus/database_md5")
virus_sequences = read_virus_database_sequences("/home/zgodek/pipr/antivirus/database_sequences")


def full_scan(path):
    path = Path(path)
    files_with_viruses = []
    for item_path in path.iterdir():
        if item_path.is_dir():
            viruses_in_folder = full_scan(item_path)
            files_with_viruses.extend(viruses_in_folder)
        if item_path.is_file():
            print(item_path)
            if check_file(item_path):
                remove_viruses(item_path, check_file(item_path))
                files_with_viruses.append(item_path)
    return files_with_viruses


def quick_scan(path, list_of_hashes={}):
    if list_of_hashes == {}:
        list_of_hashes = read_index_database("/home/zgodek/pipr/antivirus/index.json")
    path = Path(path)
    files_with_viruses = []
    for item_path in path.iterdir():
        if item_path.is_dir():
            viruses_in_folder = quick_scan(item_path, list_of_hashes)
            if viruses_in_folder != []:
                files_with_viruses.extend(viruses_in_folder)
        else:
            file = File(item_path)
            if file.hash_sh1() not in list_of_hashes.values():
                if check_file(item_path):
                    files_with_viruses.append(item_path)
    return files_with_viruses


def check_file(path):
    infected = False
    file = File(path)
    for virus_hash_md5 in virus_hashes_md5:
        if virus_hash_md5 == file.hash_md5():
            infected = True
    with open(file.path(), 'rb') as file_handle:
        byte_sequence = file_handle.read()
        for virus_sequence in virus_sequences:
            if byte_sequence.find(virus_sequence) >= 0:
                infected = True
    return infected


def remove_viruses(path):
    with open(path, 'wb') as file_handle:
        pass


def when_to_scan(time):
    pass
