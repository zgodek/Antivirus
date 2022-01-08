from pathlib import Path
import json


def read_virus_database_md5(path):
    path_database = Path(path)
    list_of_hashes = []
    for item_path in path_database.iterdir():
        with open(item_path, 'r') as file_handle:
            for line in file_handle:
                list_of_hashes.append(str(line).rstrip())
    return list_of_hashes


def read_virus_database_sequences(path):
    path_database = Path(path)
    list_of_sequences = []
    for item_path in path_database.iterdir():
        with open(item_path, 'rb') as file_handle:
            list_of_sequences.append(file_handle.read())
    return list_of_sequences


def read_index_database(path):
    list_of_hashes = []
    with open(path, 'r') as file_handle:
            data = json.load(file_handle)
            for item in data:
                list_of_hashes[item] = data[item]["hash_sh1"].rstrip()
    return list_of_hashes
