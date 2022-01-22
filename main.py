from database import Database
from scan import full_scan, quick_scan
from index import create_index, update_index, write_dict_to_index
import argparse
import json
import os


def read_config_paths():
    dict_of_paths = {}
    config_database_path = str(os.path.dirname(__file__)) + "/config_database.json"
    with open(config_database_path, 'r') as file_handle:
        data = json.load(file_handle)
        for item in data:
            dict_of_paths[item] = data[item]
    return dict_of_paths


parser = argparse.ArgumentParser(description='Perform a full scan, a quick scan, create an index of a folder or update an index of a folder')
parser.add_argument('action', type=str, help='What type of action do you want to perform')
parser.add_argument('path', type=str, help='Where do you want to perform chosen action')
args = parser.parse_args()


def main(action, path):
    database = Database(read_config_paths())
    if action == 'full scan':
        (list_of_inf_files, dict_of_updated_files) = full_scan(path, database)
        if list_of_inf_files == []:
            print("No viruses found.")
        else:
            for inf_file in list_of_inf_files:
                print(inf_file)
        write_dict_to_index(path, database, dict_of_updated_files)
    if action == 'quick scan':
        (list_of_inf_files, dict_of_updated_files) = quick_scan(path, database)
        if list_of_inf_files == []:
            print("No viruses found.")
        else:
            for inf_file in list_of_inf_files:
                print(inf_file)
        write_dict_to_index(path, database, dict_of_updated_files)
    if action == 'create index':
        create_index(path, database)
    if action == 'update index':
        update_index(path, database)
    return


if __name__ == "__main__":
    main(args.action, args.path)
