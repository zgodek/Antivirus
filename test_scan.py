import tempfile
from pathlib import Path
from scan import full_scan, quick_scan, check_file, fix_file
from io import BytesIO, StringIO


class MockDatabase:
    def __init__(self):
        pass

    def read_virus_database_md5(self):
        return (["00f538c3d410832e241486df061a57ee", "25f0ef9e7742ece45689bc91ddc1becb"])

    def read_virus_sequences_database(self):
        return ([b"aaa111", b"123456", b"8888888"])


def test_check_file_fh():
    pass


def test_check_file_clean_tempfile():
    database = MockDatabase()
    with tempfile.NamedTemporaryFile(suffix=".txt", prefix="cleantempfile") as file_handle1:
        file_handle1.write(b"This is a clean test tempfile.")
        file_handle1.seek(0)
        check_file_results = check_file(file_handle1.name, database)
    assert check_file_results[0] is False
    assert check_file_results[1] is None


def test_check_file_infected_seq_tempfile(monkeypatch):
    database = MockDatabase()
    with tempfile.NamedTemporaryFile(suffix=".txt", prefix="inftempfile") as file_handle1:
        monkeypatch.setattr('sys.stdin', StringIO('N'))
        file_handle1.write(b"sdlkadjsalkdjwow123456aaaslkdjkjaldkjsj")
        file_handle1.seek(0)
        check_file_results = check_file(file_handle1.name, database)
        assert check_file_results[0] is True
        assert check_file_results[1] == "N"


def test_fix_file():
    with tempfile.NamedTemporaryFile(suffix=".txt", prefix="infectedtempfile") as file_handle:
        fix_file(file_handle.name, b"123456aaa")
        fixed_file = file_handle.read()
        assert fixed_file.find(b'123456aaa') == -1

def test_quick_scan():
    pass
