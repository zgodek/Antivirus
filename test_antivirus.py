import tempfile
from pathlib import Path
from scan import fix_file, full_scan, quick_scan, check_file
from index import create_index, create_dict_of_files, write_dict_to_index
from database import Database
from io import StringIO
import json


def test_create_database():
    dict_of_paths = {
        "path1": "/dict/path1",
        "path2": "/dict/path2"
    }
    database = Database(dict_of_paths)
    assert database.get_path("path1") == "/dict/path1"
    assert database.get_path("path2") == "/dict/path2"
    database.change_path("path1", "/dict/path3")
    assert database.get_path("path1") == "/dict/path3"


def test_database_read_list_of_virus_hashes():
    with tempfile.TemporaryDirectory() as tmpdirname_hashes:
        with tempfile.TemporaryDirectory() as tmpdirname_sequences:
            with tempfile.NamedTemporaryFile(suffix=".txt", prefix="list_of_viruses", mode="w", dir=tmpdirname_hashes) as file_handle:
                dict_of_paths = {
                    "virus_hashes_path": tmpdirname_hashes,
                    "virus_sequences_path": tmpdirname_sequences
                }
                file_handle.write("781770fda3bd3236d0ab8274577bbbbe\n247438632580f9c018c4d8f8d9c6c408")
                file_handle.seek(0)
                database = Database(dict_of_paths)
                assert database.read_virus_database_md5() == ["781770fda3bd3236d0ab8274577bbbbe", "247438632580f9c018c4d8f8d9c6c408"]


def test_database_read_list_of_virus_sequences():
    with tempfile.TemporaryDirectory() as tmpdir_hashes:
        with tempfile.TemporaryDirectory() as tmpdir_sequences:
            dict_of_paths = {
                "virus_hashes_path": tmpdir_hashes,
                "virus_sequences_path": tmpdir_sequences
            }
            with tempfile.NamedTemporaryFile(suffix=".txt", prefix="seq1", dir=tmpdir_sequences) as file_handle1:
                with tempfile.NamedTemporaryFile(suffix=".txt", prefix="seq2", dir=tmpdir_sequences) as file_handle2:
                    file_handle1.write(b"12345")
                    file_handle1.seek(0)
                    file_handle2.write(b"$#@#@#")
                    file_handle2.seek(0)
                    database = Database(dict_of_paths)
                    assert b"12345" and b"$#@#@#" in database.read_virus_sequences_database()


def test_check_file_clean():
    with tempfile.TemporaryDirectory() as tmpdir_hashes:
        with tempfile.TemporaryDirectory() as tmpdir_sequences:
            dict_of_paths = {
                "virus_hashes_path": tmpdir_hashes,
                "virus_sequences_path": tmpdir_sequences
            }
            database = Database(dict_of_paths)
            with tempfile.NamedTemporaryFile(suffix=".txt", prefix="seq", dir=tmpdir_sequences) as file_handle0:
                file_handle0.write(b"123455")
                file_handle0.seek(0)
                with tempfile.NamedTemporaryFile(suffix=".txt", prefix="seq", mode="w", dir=tmpdir_hashes) as file_handle1:
                    file_handle1.write("00f538c3d410832e241486df061a57ee")
                    file_handle1.seek(0)
                    with tempfile.NamedTemporaryFile(suffix=".txt", prefix="cleantempfile") as file_handle1:
                        file_handle1.write(b"This is a clean test tempfile.")
                        file_handle1.seek(0)
                        check_file_results = check_file(file_handle1.name, database)
                        assert check_file_results[0] is False
                        assert check_file_results[1] is None


def test_check_file_infected_seq(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdirdatabase:
        dict_of_paths = {
            "virus_hashes_path": tmpdirdatabase,
            "virus_sequences_path": tmpdirdatabase
        }
        database = Database(dict_of_paths)
        with tempfile.NamedTemporaryFile(suffix=".txt", prefix="inftempfile") as file_handle1:
            with tempfile.NamedTemporaryFile(suffix=".txt", prefix="sequence", dir = tmpdirdatabase) as file_handle2:

                file_handle2.write(b"123456")
                file_handle2.seek(0)
                monkeypatch.setattr('sys.stdin', StringIO('N'))
                file_handle1.write(b"sdlkadjsalkdjwow123456aaaslkdjkjaldkjsj")
                file_handle1.seek(0)
                check_file_results = check_file(file_handle1.name, database)
                assert check_file_results[0] is True
                assert check_file_results[1] == "N"


def test_fix_file():
    with tempfile.NamedTemporaryFile(suffix=".txt", prefix="inftempfile") as file_handle:
        file_handle.write(b"sdlkadjsalkdjwow123456aaaslkdjkjaldkjsj")
        file_handle.seek(0)
        fix_file(file_handle.name, b"123456aaa")
        fixed_file = file_handle.read()
        assert fixed_file.find(b'123456aaa') == -1


def test_create_dict_of_files():
    with tempfile.TemporaryDirectory() as tmpdirdatabase:
        dict_of_paths = {
            "virus_hashes_path": tmpdirdatabase,
            "virus_sequences_path": tmpdirdatabase
        }
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
        write_dict_to_index("/fakedir", database, dict_of_stuff)
        with open(tmpdir_index+"/fakedir_index") as file_handle:
            data = json.load(file_handle)
            assert "name1" and "name2" in data.keys()
            for item in data:
                if item == "item1":
                    assert data[item] == {"1":"one", "2":"two"}
                elif item =="item2":
                    assert data[item] == {"3": "three"}


# def test_create_index_of_a_folder():
#     with tempfile.TemporaryDirectory() as tmpdirname:
#         database.change_path("index_path", tmpdirname)
#         with tempfile.NamedTemporaryFile(suffix=".txt", dir=tmpdirname) as file_handle1:
#             file_handle1.write(b"This is a clean test file number 1")
#             file_handle1.seek(0)
#             with tempfile.NamedTemporaryFile(suffix=".txt", dir=tmpdirname) as file_handle2:
#                 file_handle2.write(b"This is a clean test file number 2")
#                 file_handle2.seek(0)
#                 create_index(tmpdirname, database)
#                 with open(tmpdirname+"/"+os.path.split(tmpdirname)[1]+"_index", 'r') as file_handle_index:
#                     data = json.load(file_handle_index)
#                     for item in data:
#                         assert item == file_handle1.name or item == file_handle2.name
#                         assert data[item]["status"] == "Unknown"
#                         assert data[item]["last_scanned"] is None


# def test_full_scan_folder_with_infected_file(monkeypatch):
#     with tempfile.TemporaryDirectory() as tmpdirname:
#         database.change_path("index_path", tmpdirname)
#         with tempfile.NamedTemporaryFile(suffix=".txt", dir=tmpdirname) as file_handle1:
#             monkeypatch.setattr('sys.stdin', StringIO('N'))
#             file_handle1.write(b"sdlkadjsalkdjwow123456aaaslkdjkjaldkjsj")
#             file_handle1.seek(0)
#             with tempfile.NamedTemporaryFile(suffix=".txt", dir=tmpdirname) as file_handle2:
#                 file_handle2.write(b"This is a clean test file")
#                 file_handle2.seek(0)
#                 results_of_full_scan = full_scan(tmpdirname, database)
#                 for item in results_of_full_scan[1]:
#                     if item == file_handle1.name:
#                         assert results_of_full_scan[1][item]["status"] == "Infected"
#                 assert results_of_full_scan[0] == [file_handle1.name]
