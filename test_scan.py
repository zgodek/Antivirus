import tempfile
from pathlib import Path
from scan import fix_file_fh, full_scan, quick_scan, check_file
from database import Database
from io import BytesIO, StringIO


class MockDatabase:
    def __init__(self):
        pass

    def read_virus_database_md5(self, _):
        return (["00f538c3d410832e241486df061a57ee", "25f0ef9e7742ece45689bc91ddc1becb"])

    def read_virus_sequences_database(self, _):
        return ([b"aaa111", b"123456", b"8888888"])


def test_check_file_fh():
    pass


def test_check_file_clean_tempfile():
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
                with tempfile.NamedTemporaryFile(suffix=".txt", prefix="hash", mode="w", dir=tmpdir_hashes) as file_handle1:
                    file_handle1.write("00f538c3d410832e241486df061a57ee")
                    file_handle1.seek(0)
                    with tempfile.NamedTemporaryFile(suffix=".txt", prefix="cleantempfile") as file_handle1:
                        file_handle1.write(b"This is a clean test tempfile.")
                        file_handle1.seek(0)
                        check_file_results = check_file(file_handle1.name, database)
    assert check_file_results[0] is False
    assert check_file_results[1] is None


def test_check_file_infected_seq_tempfile(monkeypatch):
    with open()
        dict_of_paths = {
            "virus_hashes_path"
        }
        database = Database(dict_of_paths)
        with tempfile.NamedTemporaryFile(suffix=".txt", prefix="inftempfile") as file_handle1:
            with tempfile.NamedTemporaryFile(suffix=".txt", prefix="sequence") as file_handle2:
                file_handle2.write(b"123456")
                file_handle2.seek(0)
                monkeypatch.setattr('sys.stdin', StringIO('N'))
                file_handle1.write(b"sdlkadjsalkdjwow123456aaaslkdjkjaldkjsj")
                file_handle1.seek(0)
                check_file_results = check_file(file_handle1.name, database)
                assert check_file_results[0] is True
                assert check_file_results[1] == "N"


def test_fix_file():
    file_handle = BytesIO(b"Infected file: 123456aaa")
    file_handle = fix_file_fh(file_handle, b"123456aaa")
    fixed_file = file_handle.read()
    assert fixed_file.find(b'123456aaa') == -1

def test_quick_scan():
    pass
