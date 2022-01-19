import tempfile
from pathlib import Path
from scan import full_scan, quick_scan, check_file
from index import create_index, create_dict_of_files, write_dict_to_index
from database import Database
from io import StringIO
import os
import json


database = Database()


def test_check_file_clean():
    with tempfile.NamedTemporaryFile(suffix=".txt", prefix="cleantempfile") as file_handle:
        file_handle.write(b"This is a clean test tempfile.")
        file_handle.seek(0)
        check_file_results = check_file(file_handle.name, database)
        assert check_file_results[0] is False
        assert check_file_results[1] is None


def test_check_file_infected(monkeypatch):
    with tempfile.NamedTemporaryFile(suffix=".txt", prefix="inftempfile") as file_handle:
        monkeypatch.setattr('sys.stdin', StringIO('N'))
        file_handle.write(b"sdlkadjsalkdjwow123456aaaslkdjkjaldkjsj")
        file_handle.seek(0)
        check_file_results = check_file(file_handle.name, database)
        assert check_file_results[0] is True
        assert check_file_results[1] == "N"


def test_fix_file(monkeypatch):
    with tempfile.NamedTemporaryFile(suffix=".txt", prefix="inftempfile") as file_handle:
        monkeypatch.setattr('sys.stdin', StringIO('Y'))
        file_handle.write(b"sdlkadjsalkdjwow123456aaaslkdjkjaldkjsj")
        file_handle.seek(0)
        check_file_results = check_file(file_handle.name, database)
        assert check_file_results[0] is True
        assert check_file_results[1] == "Y"
        contents_after_check_file = file_handle.read()
        assert contents_after_check_file.find(b'123456aaa') == -1


def test_create_dict_of_files():
    with tempfile.TemporaryDirectory() as tmpdirname:
        database.change_path("index_path", tmpdirname)
        with tempfile.NamedTemporaryFile(suffix=".txt", dir=tmpdirname) as file_handle1:
            file_handle1.write(b"This is a clean test file number 1")
            file_handle1.seek(0)
            with tempfile.NamedTemporaryFile(suffix=".txt", dir=tmpdirname) as file_handle2:
                file_handle2.write(b"This is a clean test file number 2")
                file_handle2.seek(0)
                dict_of_tmp_files = create_dict_of_files(tmpdirname, database)
                assert file_handle1.name or file_handle2.name in dict_of_tmp_files.keys()


def test_write_dict_of_files():
    with tempfile.TemporaryDirectory() as tmpdirname:
        database.change_path("index_path", tmpdirname)
        with tempfile.NamedTemporaryFile(suffix=".txt", dir=tmpdirname) as file_handle1:
            file_handle1.write(b"This is a clean test file number 1")
            file_handle1.seek(0)
            with tempfile.NamedTemporaryFile(suffix=".txt", dir=tmpdirname) as file_handle2:
                file_handle2.write(b"This is a clean test file number 2")
                file_handle2.seek(0)
                dict_of_tmp_files = create_dict_of_files(tmpdirname, database)
                write_dict_to_index(tmpdirname, database, dict_of_tmp_files)
                with open(tmpdirname+"/"+os.path.split(tmpdirname)[1]+"_index", 'r') as file_handle_index:
                    data = json.load(file_handle_index)
                    for item in data:
                        assert item == file_handle1.name or item == file_handle2.name


def test_create_index_of_a_folder():
    with tempfile.TemporaryDirectory() as tmpdirname:
        database.change_path("index_path", tmpdirname)
        with tempfile.NamedTemporaryFile(suffix=".txt", dir=tmpdirname) as file_handle1:
            file_handle1.write(b"This is a clean test file number 1")
            file_handle1.seek(0)
            with tempfile.NamedTemporaryFile(suffix=".txt", dir=tmpdirname) as file_handle2:
                file_handle2.write(b"This is a clean test file number 2")
                file_handle2.seek(0)
                create_index(tmpdirname, database)
                with open(tmpdirname+"/"+os.path.split(tmpdirname)[1]+"_index", 'r') as file_handle_index:
                    data = json.load(file_handle_index)
                    for item in data:
                        assert item == file_handle1.name or item == file_handle2.name
                        assert data[item]["status"] == "Unknown"
                        assert data[item]["last_scanned"] is None


def test_full_scan_folder_with_infected_file(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdirname:
        database.change_path("index_path", tmpdirname)
        with tempfile.NamedTemporaryFile(suffix=".txt", dir=tmpdirname) as file_handle1:
            monkeypatch.setattr('sys.stdin', StringIO('N'))
            file_handle1.write(b"sdlkadjsalkdjwow123456aaaslkdjkjaldkjsj")
            file_handle1.seek(0)
            with tempfile.NamedTemporaryFile(suffix=".txt", dir=tmpdirname) as file_handle2:
                file_handle2.write(b"This is a clean test file")
                file_handle2.seek(0)
                results_of_full_scan = full_scan(tmpdirname, database)
                write_dict_to_index(database.get_path("index_path"), database, results_of_full_scan[1])
                with open(tmpdirname+"/"+os.path.split(tmpdirname)[1]+"_index", 'r') as file_handle_index:
                    data = json.load(file_handle_index)
                    for item in data:
                        if item == file_handle1.name:
                            assert data[item]["status"] == "Infected"
                assert results_of_full_scan[0] == [file_handle1.name]
