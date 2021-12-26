import hashlib


def hash_a_file(path):
    BLOCKSIZE = 65536
    hasher = hashlib.sha1()
    with open(path, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return(hasher.hexdigest())
