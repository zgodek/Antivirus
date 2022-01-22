import tempfile
from file import hash_md5_bytes
from scan import check_file_fh, full_scan, quick_scan, check_file, fix_file
from io import BytesIO, StringIO
import pytest
from scan import PathDoesntExistError


class MockDatabase:
    def __init__(self):
        self._virus_hashes = ["00f538c3d410832e241486df061a57ee", "25f0ef9e7742ece45689bc91ddc1becb"]
        self._virus_sequences = [b"aaa111", b"hahahah", b"8888888"]

    def read_virus_database_md5(self):
        return (self._virus_hashes)

    def read_virus_sequences_database(self):
        return (self._virus_sequences)

    def add_virus_hash(self, hash):
        self._virus_hashes.append(hash)

    def read_index_database(self, path):
        return {}

    def get_paths(self):
        return []


def test_check_file_fh_clean():
    database = MockDatabase()
    file_handle = BytesIO(b"This is a clean file.")
    (infected, found_virus_seq) = check_file_fh(file_handle, database.read_virus_database_md5(), database.read_virus_sequences_database())
    assert infected == False
    assert found_virus_seq == []


def test_check_file_fh_infected_seq():
    database = MockDatabase()
    file_handle = BytesIO(b"sadskalaaa111dj")
    (infected, found_virus_seq) = check_file_fh(file_handle, database.read_virus_database_md5(), database.read_virus_sequences_database())
    assert infected == True
    assert found_virus_seq == [b"aaa111"]


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
        file_handle1.write(b"sdlkadjsalkdjwow1888888823456aaaslkdjkjaldkjsj")
        file_handle1.seek(0)
        check_file_results = check_file(file_handle1.name, database)
        assert check_file_results[0] is True
        assert check_file_results[1] == "N"


def test_check_file_virusfile(monkeypatch):
    database = MockDatabase()
    with tempfile.NamedTemporaryFile() as file_handle:
        monkeypatch.setattr('sys.stdin', StringIO('N'))
        file_handle.write(b"AAAAAAAAAAAA")
        file_handle.seek(0)
        database.add_virus_hash(hash_md5_bytes(b"AAAAAAAAAAAA"))
        assert check_file(file_handle.name, database)[0] is True


def test_fix_file():
    with tempfile.NamedTemporaryFile(suffix=".txt", prefix="infectedtempfile") as file_handle:
        file_handle.write(b"asjdhsaskjdhaskjdshkhdhkasjhdkjaaaaaaaaaasdsldaslkdjklas")
        file_handle.seek(0)
        fix_file(file_handle.name, b"aaaaaaaaa")
        fixed_file = file_handle.read()
        assert fixed_file.find(b'aaaaaaaaa') == -1


def test_full_scan_wrong_path():
    database = MockDatabase()
    with pytest.raises(PathDoesntExistError):
        full_scan("/fakepath", database)


def test_full_scan_one_folder_clean_without_index():
    database = MockDatabase()
    with tempfile.TemporaryDirectory() as tempdir:
        with tempfile.NamedTemporaryFile(suffix=".txt", prefix="cleanfile1", dir=tempdir) as file_handle1:
            with tempfile.NamedTemporaryFile(suffix=".txt", prefix="cleanfile2", dir=tempdir) as file_handle2:
                with tempfile.NamedTemporaryFile(suffix=".txt", prefix="cleanfile3", dir=tempdir) as file_handle3:
                    file_handle1.write(b"This is a clean file number 1.")
                    file_handle2.write(b"This is a clean file number 2.")
                    file_handle3.write(b"This is a clean file number 3.")
                    file_handle1.seek(0)
                    file_handle2.seek(0)
                    file_handle3.seek(0)
                    (files_with_viruses, dict_of_files) = full_scan(tempdir, database)
                    assert files_with_viruses == []
                    for file in dict_of_files:
                        assert dict_of_files[file]["last_scanned"] is not None


def test_full_scan_one_folder_clean_with_index():
    database = MockDatabase()
    with tempfile.TemporaryDirectory() as tempdir:
        with tempfile.NamedTemporaryFile(suffix=".txt", prefix="cleanfile1", dir=tempdir) as file_handle1:
            with tempfile.NamedTemporaryFile(suffix=".txt", prefix="cleanfile2", dir=tempdir) as file_handle2:
                with tempfile.NamedTemporaryFile(suffix=".txt", prefix="cleanfile3", dir=tempdir) as file_handle3:
                    file_handle1.write(b"This is a clean file number 1.")
                    file_handle2.write(b"This is a clean file number 2.")
                    file_handle3.write(b"This is a clean file number 3.")
                    file_handle1.seek(0)
                    file_handle2.seek(0)
                    file_handle3.seek(0)
                    dict_of_files = {
                        file_handle1.name: {
                            "status": "Unknown",
                            "hash_md5": hash_md5_bytes(file_handle1.read()),
                            "last_scanned": None
                        },
                        file_handle2.name: {
                            "status": "Unknown",
                            "hash_md5": hash_md5_bytes(file_handle2.read()),
                            "last_scanned": None
                        },
                        file_handle3.name: {
                            "status": "Unknown",
                            "hash_md5": hash_md5_bytes(file_handle3.read()),
                            "last_scanned": None
                        }
                    }
                    (files_with_viruses, dict_of_files) = full_scan(tempdir, database)
                    assert files_with_viruses == []
                    for file in dict_of_files:
                        assert dict_of_files[file]["last_scanned"] is not None
