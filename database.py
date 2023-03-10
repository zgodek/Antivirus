from pathlib import Path, PurePath
import json
import os


class DictionaryError(Exception):
    def __init__(self, message):
        super().__init__(message)


class IndexError(Exception):
    def __init__(self, message):
        super().__init__(message)


class Database:
    def __init__(self, dict_of_paths):
        if type(dict_of_paths) != dict:
            raise DictionaryError("A dictionary is required to create this database.")
        self._dict_of_paths = dict_of_paths

    def get_path(self, which_path):
        return self._dict_of_paths[which_path]

    def get_paths(self):
        """
        returns values from dict_of_paths as a list
        """
        list_of_paths = []
        for path in self._dict_of_paths:
            list_of_paths.append(Path(self._dict_of_paths[path]))
        return list_of_paths

    def read_virus_database_md5(self):
        """
        reads hashes from files in a folder which path is saved in
        self._dict_of_paths["virus_hashes_path"]
        """
        path = self.get_path("virus_hashes_path")
        path_database = Path(path)
        list_of_hashes = []
        if path_database.is_dir():
            for item_path in path_database.iterdir():
                with open(item_path, 'r') as file_handle:
                    for line in file_handle:
                        list_of_hashes.append(str(line).rstrip())
        else:
            with open(path, 'r') as file_handle:
                for line in file_handle:
                    list_of_hashes.append(str(line).rstrip())
        return list_of_hashes

    def read_virus_sequences_database(self):
        """
        reads sequences of bytes from files in a folder which path is saved in
        self._dict_of_paths["virus_sequences_path"] and then returns them
        in a list
        """
        path = self.get_path("virus_sequences_path")
        path_database = Path(path)
        list_of_sequences = []
        for item_path in path_database.iterdir():
            with open(item_path, 'rb') as file_handle:
                list_of_sequences.append(file_handle.read())
        return list_of_sequences

    def read_index_database(self, path):
        """
        reads an index of a given path from a folder of index files, which path
        is saved in self._dict_of_paths["index_path"] and returns its contents
        """
        path = PurePath(path)
        path = self.get_path("index_path")+f'/{path.name}_index'
        if not os.path.isfile(path):
            raise IndexError("Index for this folder does not exist")
        dict_of_files = {}
        with open(path, 'r') as file_handle:
            data = json.load(file_handle)
            for item in data:
                dict_of_files[str(item)] = data[str(item)]
        return dict_of_files
