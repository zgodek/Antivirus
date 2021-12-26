import hashlib
import os
from pathlib import Path


def hash_a_file(path):
    if os.path.isfile(path):
        BLOCKSIZE = 65536
        hasher = hashlib.sha1()
        with open(path, 'rb') as afile:
            buf = afile.read(BLOCKSIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = afile.read(BLOCKSIZE)
        return hasher.hexdigest()
    else:
        return None


def hash_a_folder(path):
    p = Path(path)
    for x in p.iterdir():
        if x.is_dir():
            hash_a_folder(x)
        elif x.is_file():
            BLOCKSIZE = 65536
            hasher = hashlib.sha1()
            with open(x, 'rb') as afile:
                buf = afile.read(BLOCKSIZE)
                while len(buf) > 0:
                    hasher.update(buf)
                    buf = afile.read(BLOCKSIZE)
            print(hasher.hexdigest())
        else:
            return('Incorrect path.')
