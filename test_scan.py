import tempfile
from scan import check_file_fh, full_scan, quick_scan, check_file, fix_file
from io import BytesIO, StringIO
import pytest
from scan import PathDoesntExistError
import time
import hashlib


class MockDatabase:
    def __init__(self):
        self._virus_hashes = ["00f538c3d410832e241486df061a57ee",
                              "25f0ef9e7742ece45689bc91ddc1becb"]
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


def test_fix_file():
    with tempfile.NamedTemporaryFile() as file_handle:
        file_handle.write(b"asjdhsasjhdkjaaaaaaaaaasdsldaslkdjklas")
        file_handle.seek(0)
        fix_file(file_handle.name, b"aaaaaaaaa")
        fixed_file = file_handle.read()
        assert fixed_file.find(b'aaaaaaaaa') == -1


def test_check_file_fh_clean():
    database = MockDatabase()
    file_handle = BytesIO(b"This is a clean file.")
    (infected, found_virus_seq) = check_file_fh(
        file_handle,
        database.read_virus_database_md5(),
        database.read_virus_sequences_database())
    assert infected is False
    assert found_virus_seq == []


def test_check_file_fh_infected_seq():
    database = MockDatabase()
    file_handle = BytesIO(b"sadskalaaa111dj")
    (infected, found_virus_seq) = check_file_fh(
        file_handle,
        database.read_virus_database_md5(),
        database.read_virus_sequences_database())
    assert infected is True
    assert found_virus_seq == [b"aaa111"]


def test_check_file_virus_hash():
    database = MockDatabase()
    byte_code = b"fdsfdfasdasd"
    file_handle = BytesIO(byte_code)
    hasher = hashlib.md5()
    hasher.update(byte_code)
    hash = hasher.hexdigest()
    database.add_virus_hash(hash)
    (infected, found_virus_seq) = check_file_fh(file_handle, database.read_virus_database_md5(), database.read_virus_sequences_database())
    assert infected is True
    assert found_virus_seq == []


def test_check_file_clean_tempfile():
    database = MockDatabase()
    with tempfile.NamedTemporaryFile() as file_handle1:
        file_handle1.write(b"This is a clean test tempfile.")
        file_handle1.seek(0)
        (is_infected, is_fixed) = check_file(
            file_handle1.name,
            database.read_virus_database_md5(),
            database.read_virus_sequences_database())
    assert is_infected is False
    assert is_fixed is None


def test_check_file_infected_seq_tempfile(monkeypatch):
    database = MockDatabase()
    with tempfile.NamedTemporaryFile() as file_handle1:
        monkeypatch.setattr('sys.stdin', StringIO('N'))
        file_handle1.write(b"sdlkadjsalkdjwow1888888823456aaaslkdjkjaldkjsj")
        file_handle1.seek(0)
        (is_infected, is_fixed) = check_file(
            file_handle1.name,
            database.read_virus_database_md5(),
            database.read_virus_sequences_database())
    assert is_infected is True
    assert is_fixed is False


def test_check_file_virusfile(monkeypatch):
    database = MockDatabase()
    with tempfile.NamedTemporaryFile() as file_handle:
        monkeypatch.setattr('sys.stdin', StringIO('N'))
        file_handle.write(b"AAAAAAAAAAAA")
        file_handle.seek(0)
        hasher = hashlib.md5()
        hasher.update(b"AAAAAAAAAAAA")
        hash = hasher.hexdigest()
        database.add_virus_hash(hash)
        (is_infected, is_fixed) = check_file(
            file_handle.name,
            database.read_virus_database_md5(),
            database.read_virus_sequences_database())
    assert is_infected is True
    assert is_fixed is False


def test_full_scan_wrong_path():
    database = MockDatabase()
    with pytest.raises(PathDoesntExistError):
        full_scan("/fakepath", database)


def test_full_scan_clean_without_index():
    time_right_now = time.time()
    database = MockDatabase()
    with tempfile.TemporaryDirectory() as tempdir, \
            tempfile.NamedTemporaryFile(dir=tempdir) as file_handle1, \
            tempfile.NamedTemporaryFile(dir=tempdir) as file_handle2, \
            tempfile.NamedTemporaryFile(dir=tempdir) as file_handle3:
        file_handle1.write(b"This is a clean file number 1.")
        file_handle2.write(b"This is a clean file number 2.")
        file_handle3.write(b"This is a clean file number 3.")
        file_handle1.seek(0)
        file_handle2.seek(0)
        file_handle3.seek(0)
        (files_with_viruses, dict_of_files) = full_scan(tempdir, database)
        assert files_with_viruses == []
        for file in dict_of_files:
            assert dict_of_files[file]["last_scanned"] > time_right_now
            assert dict_of_files[file]["status"] == "Clean"


def test_full_scan_clean_with_index():
    database = MockDatabase()
    with tempfile.TemporaryDirectory() as tempdir, \
            tempfile.NamedTemporaryFile(dir=tempdir) as file_handle1, \
            tempfile.NamedTemporaryFile(dir=tempdir) as file_handle2, \
            tempfile.NamedTemporaryFile(dir=tempdir) as file_handle3:
        file_handle1.write(b"fhis a clesmdlksmd filedsd number")
        file_handle2.write(b"Thww ssdsan fidsle dasdw1e1we1e1er")
        file_handle3.write(b"hisads i12s 1213123231j23i2a an mber")
        file_handle1.seek(0)
        file_handle2.seek(0)
        file_handle3.seek(0)
        hasher = hashlib.md5()
        hasher.update(file_handle1.read())
        hash1 = hasher.hexdigest()
        hasher = hashlib.md5()
        hasher.update(file_handle2.read())
        hash2 = hasher.hexdigest()
        hasher = hashlib.md5()
        hasher.update(file_handle3.read())
        hash3 = hasher.hexdigest()
        dict_of_files = {
            file_handle1.name: {
                "status": "Unknown",
                "hash_md5": hash1,
                "last_scanned": None
            },
            file_handle2.name: {
                "status": "Unknown",
                "hash_md5": hash2,
                "last_scanned": None
            },
            file_handle3.name: {
                "status": "Unknown",
                "hash_md5": hash3,
                "last_scanned": None
            }
        }
        (files_with_viruses, dict_of_files) = full_scan(tempdir, database)
        assert files_with_viruses == []
        for file in dict_of_files:
            assert dict_of_files[file]["last_scanned"] is not None
            assert dict_of_files[file]["status"] == "Clean"


def test_full_scan_clean_with_recursion():
    database = MockDatabase()
    with tempfile.TemporaryDirectory() as tempdir1, \
            tempfile.TemporaryDirectory(dir=tempdir1) as tempdir2, \
            tempfile.NamedTemporaryFile(dir=tempdir1) as file_handle1, \
            tempfile.NamedTemporaryFile(dir=tempdir2) as file_handle2:
        file_handle1.write(b"122kmlkwlkaslkdjso9023isdklasd")
        file_handle2.write(b"ldkmwij10j03j2owd")
        file_handle1.seek(0)
        file_handle2.seek(0)
        (files_with_viruses, dict_of_files) = full_scan(tempdir2, database)
        assert files_with_viruses == []
        for file in dict_of_files:
            assert dict_of_files[file]["last_scanned"] is not None
            assert dict_of_files[file]["status"] == "Clean"


def test_quick_scan():
    database = MockDatabase()
    with tempfile.TemporaryDirectory() as tempdir1, \
            tempfile.TemporaryDirectory(dir=tempdir1) as tempdir2, \
            tempfile.NamedTemporaryFile(dir=tempdir1) as file_handle1, \
            tempfile.NamedTemporaryFile(dir=tempdir2) as file_handle2:
        hasher = hashlib.md5()
        hasher.update(file_handle1.read())
        hash1 = hasher.hexdigest()
        hasher = hashlib.md5()
        hasher.update(file_handle2.read())
        hash2 = hasher.hexdigest()
        index = {
            file_handle1.name: {
                "status": "Clean",
                "hash_md5": hash1,
                "last_scanned": time.time()
            },
            file_handle2.name: {
                "status": "Unknown",
                "hash_md5": hash2,
                "last_scanned": time.time()
            }
        }
        time_before_scan = time.time()
        time.sleep(0.01)
        (files_with_viruses, dict_of_files) = quick_scan(tempdir1, database, index)
        assert files_with_viruses == []
        assert file_handle1.name and file_handle2.name in dict_of_files.keys()
        assert dict_of_files[file_handle1.name]["status"] == "Clean"
        assert dict_of_files[file_handle2.name]["status"] == "Clean"
        assert dict_of_files[file_handle2.name]["last_scanned"] > time_before_scan
        assert dict_of_files[file_handle1.name]["last_scanned"] < time_before_scan
