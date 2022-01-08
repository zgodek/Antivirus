from pathlib import Path
import json
from file import File


def create_a_list_of_files(path):
    list_of_files = []
    path = Path(path)
    for item_path in path.iterdir():
        if item_path.is_dir():
            for file in create_a_list_of_files(item_path):
                list_of_files.append(file)
        elif item_path.is_file():
            list_of_files.append(File(item_path))
    return list_of_files


def save_index_to_json(path):
    list_of_files = create_a_list_of_files(path)
    with open("/home/zgodek/pipr/antivirus/index.json", 'w') as file_handle:
        data = {}
        for file in list_of_files:
            file_data = {
                # "status": str(file.status()),
                "hash_md5": str(file.hash_md5()),
                "hash_sh1": str(file.hash_sh1())
            }
            data[str(file.path())] = file_data
        json.dump(data, file_handle)


def update_index_in_json(path, filepath):
    with open(path, 'r') as file_handle:
        data = json.load(file_handle)
    file = File(filepath)
    with open(path, 'w') as file_handle:
        data[filepath] = {
            # "status": str(file.status()),
            "hash_md5": str(file.hash_md5()),
            "hash_sh1": str(file.hash_sh1())
        }
        json.dump(data, file_handle)
