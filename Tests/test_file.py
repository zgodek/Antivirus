import tempfile
from file import File, hash_md5_bytes


def test_create_file():
    file = File("/fake/path")
    assert file.path() == "/fake/path"
    assert file.status() == "Unknown"


def test_compare_hash_file_to_hash_code():
    with tempfile.NamedTemporaryFile() as file_handle:
        file_handle.write(b"1234kajkshdkjsah")
        file_handle.seek(0)
        code = b"1234kajkshdkjsah"
        file = File(file_handle.name)
        assert hash_md5_bytes(code) == file.hash_md5()
