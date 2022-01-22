import tempfile
from pathlib import Path
from index import create_index, create_dict_of_files, write_dict_to_index
from database import Database
import json


def test_create_dict_of_files():
    dict_of_paths = {}
    database = Database(dict_of_paths)
    with tempfile.TemporaryDirectory() as tmpdirname:
        with tempfile.NamedTemporaryFile(suffix=".txt", dir=tmpdirname) as file_handle1:
            file_handle1.write(b"This is a clean test file number 1")
            file_handle1.seek(0)
            with tempfile.NamedTemporaryFile(suffix=".txt", dir=tmpdirname) as file_handle2:
                file_handle2.write(b"This is a clean test file number 2")
                file_handle2.seek(0)
                dict_of_tmp_files = create_dict_of_files(tmpdirname, database)
                assert file_handle1.name or file_handle2.name in dict_of_tmp_files.keys()


def test_write_dict_to_index():
    with tempfile.TemporaryDirectory() as tmpdir_index:
        dict_of_paths = {
            "index_path": tmpdir_index
        }
        database = Database(dict_of_paths)
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
    with tempfile.TemporaryDirectory() as tmpdir_index:
        dict_of_paths = {
            "index_path": tmpdir_index
        }
        database = Database(dict_of_paths)
        with tempfile.TemporaryDirectory() as tmpdir_files:
            with tempfile.NamedTemporaryFile(suffix=".txt", dir=tmpdir_files) as file_handle1:
                with tempfile.NamedTemporaryFile(suffix=".txt", dir=tmpdir_files) as file_handle2:
                    create_index(tmpdir_files, database)
                    tmpdir_index = Path(tmpdir_index)
                    for file in tmpdir_index.iterdir():
                        with open(file.as_posix()) as file_handle_index:
                            index = json.load(file_handle_index)
                            list_of_file_paths_in_index = []
                            for file in index:
                                list_of_file_paths_in_index.append(file)
                            assert file_handle1.name and file_handle2.name in list_of_file_paths_in_index