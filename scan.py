from pathlib import Path
from file import File


def full_scan(path, database_fs):
    path = Path(path)
    files_with_viruses = []
    for item_path in path.iterdir():
        if item_path == Path(database_fs.get_path("virus_sequences_path")) or item_path == Path(database_fs.get_path("virus_hashes_path")):
            continue
        if item_path.is_dir():
            viruses_in_folder = full_scan(item_path, database_fs)
            files_with_viruses.extend(viruses_in_folder)
        if item_path.is_file():
            if check_file(item_path, database_fs):
                files_with_viruses.append(item_path)
    return files_with_viruses


def quick_scan(path, database_qs, dict_of_hashes=None):
    if dict_of_hashes is None:
        dict_of_hashes = database_qs.read_index_database()
        if dict_of_hashes == -1:
            pass#jakis Error
    path = Path(path)
    files_with_viruses = []
    for item_path in path.iterdir():
        if item_path == Path(database_qs.get_path("virus_sequences_path")) or item_path == Path(database_qs.get_path("virus_hashes_path")):
            continue
        if item_path.is_dir():
            viruses_in_folder = quick_scan(item_path, database_qs, dict_of_hashes)
            if viruses_in_folder != []:
                files_with_viruses.extend(viruses_in_folder)
        else:
            file = File(item_path)
            if file.hash_sh1() not in dict_of_hashes.values():
                if check_file(item_path, database_qs):
                    files_with_viruses.append(item_path)
    return files_with_viruses


def check_file(path, database_chf):
    infected = False
    file = File(path)
    virus_hashes_md5 = database_chf.read_virus_database_md5()
    virus_sequences = database_chf.virus_sequences_database()
    for virus_hash_md5 in virus_hashes_md5:
        if virus_hash_md5 == file.hash_md5():
            infected = True
    with open(file.path(), 'rb') as file_handle:
        byte_sequence = file_handle.read()
        for virus_sequence in virus_sequences:
            position = byte_sequence.find(virus_sequence)
            if position >= 0:
                infected = True
    return infected


def remove_file(path):
    pass
    # os.remove(path)


def fix_file(path, virus_sequence):
    with open(path, 'rb') as file_handle:
        file_code_string = str(file_handle.read())
        file_code_string.replace(str(virus_sequence), "")
    with open(path, 'wb') as file_handle:
        file_handle.write(bytes(file_code_string, "utf-8"))


# fix_file("/home/zgodek/project_pipr/antivirus/susfile.txt", "aaa")
