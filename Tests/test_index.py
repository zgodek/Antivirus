import tempfile
from pathlib import Path
from index import create_index, create_dict_of_files, write_dict_to_index, have_files_changed
import json
import time


class MockDatabase:
    def __init__(self, index_path=""):
        self._index_path = index_path

    def read_index_database(self, path):
        index_path = Path(self._index_path)
        for item_path in index_path.iterdir():
            item_path = item_path.as_posix()
            with open(item_path, 'r') as file_handle:
                return json.load(file_handle)

    def get_path(self, path):
        if path == "index_path":
            return self._index_path

    def get_paths(self):
        return []


def test_create_dict_of_files():
    database = MockDatabase()
    with tempfile.TemporaryDirectory() as tmpdirname, \
            tempfile.NamedTemporaryFile(dir=tmpdirname) as file_handle1, \
            tempfile.NamedTemporaryFile(dir=tmpdirname) as file_handle2:
        file_handle1.write(b"This is a clean test file number 1")
        file_handle1.seek(0)
        file_handle2.write(b"This is a clean test file number 2")
        file_handle2.seek(0)
        dict_of_tmp_files = create_dict_of_files(tmpdirname, database)
        assert file_handle1.name or file_handle2.name in dict_of_tmp_files.keys()


def test_write_dict_to_index():
    with tempfile.TemporaryDirectory() as tmpdir_index:
        database = MockDatabase(tmpdir_index)
        dict_of_stuff = {
            "name1": {"1": "one", "2": "two"},
            "name2": {"3": "three"}
        }
        write_dict_to_index("/fake_dir", database, dict_of_stuff)
        with open(tmpdir_index+"/fake_dir_index") as file_handle:
            data = json.load(file_handle)
            assert "name1" and "name2" in data.keys()
            for item in data:
                if item == "item1":
                    assert data[item] == {"1": "one", "2": "two"}
                elif item == "item2":
                    assert data[item] == {"3": "three"}


def test_create_index():
    with tempfile.TemporaryDirectory() as tmpdir_index, \
            tempfile.TemporaryDirectory() as tmpdir_files, \
            tempfile.NamedTemporaryFile(dir=tmpdir_files) as file_handle1, \
            tempfile.NamedTemporaryFile(dir=tmpdir_files) as file_handle2:
        database = MockDatabase(tmpdir_index)
        create_index(tmpdir_files, database)
        tmpdir_index = Path(tmpdir_index)
        for file in tmpdir_index.iterdir():
            with open(file.as_posix()) as file_handle_index:
                index = json.load(file_handle_index)
                list_of_file_paths_in_index = []
                for file in index:
                    list_of_file_paths_in_index.append(file)
                assert file_handle1.name and file_handle2.name in list_of_file_paths_in_index


def test_have_files_changed():
    with tempfile.TemporaryDirectory() as tmpdir_index, \
            tempfile.TemporaryDirectory() as dir_with_files, \
            tempfile.NamedTemporaryFile(suffix="_index", mode="w+", dir=tmpdir_index) as file_handle_index, \
            tempfile.NamedTemporaryFile(dir=dir_with_files) as file_handle1, \
            tempfile.NamedTemporaryFile(dir=dir_with_files) as file_handle2:
        database = MockDatabase(tmpdir_index)
        index_dict = {
            file_handle1.name: {
                "status": "Clean",
                "hash_md5": "some_hash",
                "last_scanned": time.time()
            },
            file_handle2.name: {
                "status": "Clean",
                "hash_md5": "some_hash",
                "last_scanned": time.time()
            }
        }
        time.sleep(0.01)
        json.dump(index_dict, file_handle_index)
        file_handle_index.flush()
        file_handle1.write(b"12323123213")
        file_handle1.seek(0)
        dict_of_files = have_files_changed(dir_with_files, database)
        assert file_handle1.name and file_handle2.name in dict_of_files.keys()
        assert dict_of_files[file_handle1.name]["status"] == "Unknown"
        assert dict_of_files[file_handle2.name]["status"] == "Clean"
