from pathlib import Path
import json


class Database:
    def __init__(self):
        self._dict_of_paths = {
            "virus_hashes_path": "/home/zgodek/pipr/antivirus/database_md5",
            "virus_sequences_path": "/home/zgodek/pipr/antivirus/database_sequences",
            "index_path": "/home/zgodek/pipr/antivirus/index.json"
        }

    def change_path(self, which_path, new_path):
        self._dict_of_paths[which_path] = new_path

    def get_path(self, which_path):
        return self._dict_of_paths[which_path]

    def read_virus_database_md5(self):
        path = self.get_path("virus_hashes_path")
        path_database = Path(path)
        list_of_hashes = []
        for item_path in path_database.iterdir():
            with open(item_path, 'r') as file_handle:
                for line in file_handle:
                    list_of_hashes.append(str(line).rstrip())
        return list_of_hashes

    def virus_sequences_databse(self):
        path = self.get_path("virus_sequences_path")
        path_database = Path(path)
        list_of_sequences = []
        for item_path in path_database.iterdir():
            with open(item_path, 'rb') as file_handle:
                list_of_sequences.append(file_handle.read())
        return list_of_sequences

    def read_index_database(self):
        path = self.get_path("index_path")
        dict_of_hashes = {}
        with open(path, 'r') as file_handle:
            data = json.load(file_handle)
            for item in data:
                dict_of_hashes[str(item)] = data[str(item)]["hash_sh1"]
        return dict_of_hashes
