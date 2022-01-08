from pathlib import Path
import json
from file import File


def check_file(path):
    infected = False
    file = File(path)
    path_database = '/home/zgodek/pipr/antivirus/database_md5'
    path_database = Path(path_database)
    for item_path in path_database.iterdir():
        with open(item_path, 'r') as file_handle:
            for line in file_handle:
                if str(line).rstrip() == str(file.hash_md5()):
                    infected = True
    with open(path, 'rb') as file_handle:
        pass
    return infected


def full_scan(path):
    path = Path(path)
    files_with_viruses = []
    for item_path in path.iterdir():
        if item_path.is_dir():
            viruses_in_folder = full_scan(item_path)
            files_with_viruses.extend(viruses_in_folder)
        if item_path.is_file():
            print(item_path)
            if check_file(item_path):
                remove_viruses(item_path, check_file(item_path))
                files_with_viruses.append(item_path)
    return files_with_viruses


def quick_scan(path, list_of_hashes={}):
    if list_of_hashes == {}:
        with open("/home/zgodek/pipr/antivirus/index.json", 'r') as file_handle:
            data = json.load(file_handle)
            for item in data:
                list_of_hashes[item] = data[item]["hash_sh1"]
    path = Path(path)
    files_with_viruses = []
    for item_path in path.iterdir():
        if item_path.is_dir():
            viruses_in_folder = quick_scan(item_path, list_of_hashes)
            if viruses_in_folder != []:
                files_with_viruses.extend(viruses_in_folder)
        else:
            file = File(item_path)
            if file.hash_md5() not in list_of_hashes:
                if check_file(item_path):
                    files_with_viruses.append(item_path)
    return files_with_viruses


def remove_viruses(path, location):
    with open(path, 'wb') as file_handle:
        pass


def when_to_scan(time):
    pass
