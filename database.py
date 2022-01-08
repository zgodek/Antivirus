from pathlib import Path
import json


def read_virus_database(path):
    path_database = Path(path)
    list_of_items = []
    for item_path in path_database.iterdir():
        with open(item_path, 'r') as file_handle:
            for line in file_handle:
                list_of_items.append(str(line).rstrip())
    return list_of_items


def read_index_database(path):
    list_of_hashes = []
    with open(path, 'r') as file_handle:
            data = json.load(file_handle)
            for item in data:
                list_of_hashes[item] = data[item]["hash_sh1"].rstrip()
    return list_of_hashes
