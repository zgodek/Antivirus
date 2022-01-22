import tempfile
from pathlib import Path
from database import Database
import os


def test_database_get_path():
    dict_of_paths = {
        "path1": "/dir/path1",
        "path2": "/dir/path2"
    }
    database = Database(dict_of_paths)
    assert database.get_path("path1") == "/dir/path1"
    assert database.get_path("path2") == "/dir/path2"


def test_database_get_paths():
    dict_of_paths = {
        "path1": "/dir/path1",
        "path2": "/dir/path2"
    }
    database = Database(dict_of_paths)
    assert database.get_paths() == [Path("/dir/path1"), Path("/dir/path2")]


def test_database_read_virus_hashes():
    with tempfile.TemporaryDirectory() as tmpdirname_hashes:
        with tempfile.NamedTemporaryFile(suffix=".txt", prefix="list_of_viruses", mode="w", dir=tmpdirname_hashes) as file_handle:
            dict_of_paths = {
                "virus_hashes_path": tmpdirname_hashes,
            }
            file_handle.write("781770fda3bd3236d0ab8274577bbbbe\n247438632580f9c018c4d8f8d9c6c408")
            file_handle.seek(0)
            database = Database(dict_of_paths)
            assert database.read_virus_database_md5() == ["781770fda3bd3236d0ab8274577bbbbe", "247438632580f9c018c4d8f8d9c6c408"]


def test_database_read_virus_sequences():
    with tempfile.TemporaryDirectory() as tmpdir_sequences:
        dict_of_paths = {
            "virus_sequences_path": tmpdir_sequences
        }
        database = Database(dict_of_paths)
        with tempfile.NamedTemporaryFile(suffix=".txt", prefix="seq1", dir=tmpdir_sequences) as file_handle1:
            with tempfile.NamedTemporaryFile(suffix=".txt", prefix="seq2", dir=tmpdir_sequences) as file_handle2:
                file_handle1.write(b"12345")
                file_handle1.seek(0)
                file_handle2.write(b"$#@#@#")
                file_handle2.seek(0)
                assert b"12345" and b"$#@#@#" in database.read_virus_sequences_database()


def test_database_read_index():
    with tempfile.TemporaryDirectory() as tmpdirindex:
        dict_of_paths = {
            "index_path": tmpdirindex
        }
        database = Database(dict_of_paths)
        with tempfile.NamedTemporaryFile(mode="w", dir=tmpdirindex) as file_handle:
            os.link(file_handle.name, tmpdirindex+"/folderindex_index")
            test_dict = {'path1': {'key1': 'value1', 'key2': 'value2'}, 'path2': {'key3': 'value3', 'key4': 'value4'}}
            file_handle.write(f"{test_dict}")
            file_handle.seek(0)
            path = file_handle.name.replace("_index", "")
            assert database.read_index_database(path) == test_dict
