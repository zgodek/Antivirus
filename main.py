from random import choice
from database import Database
from scan import full_scan, quick_scan
from index import create_index, update_index, write_dict_to_index
from cron_setup import enable_autoscan, disable_autoscan
import argparse
import json
import os


def read_config_paths():
    """
    reads config_database.json file and returns its contents in a dictionary
    """
    dict_of_paths = {}
    config_database_path = str(os.path.dirname(__file__)) + "/config_database.json"
    with open(config_database_path, 'r') as file_handle:
        data = json.load(file_handle)
        for item in data:
            dict_of_paths[item] = data[item]
    return dict_of_paths


parser = argparse.ArgumentParser(description="Perform a full scan, a quick" +
                                 " scan, create an index, update an index of" +
                                 " a path or enable and disable a regular" +
                                 " quick scan of a path which is performed in given" +
                                 " time intervals")
subparsers = parser.add_subparsers()
scan_parser = subparsers.add_parser("scan", help="Perform one of possible scans")
index_parser = subparsers.add_parser("index", help="Update or create an index")
autoscan_parser = subparsers.add_parser("autoscan", help="Schedule future regular quick scans")
scan_parser.add_argument("type_of_scan", choices=['quick', 'full'], help="Choose type of scan")
index_parser.add_argument("type_of_index_operation", choices=['create', 'update'],
                          help="Choose whether you want to create or update an index")
autoscan_parser.add_argument("type_of_action", choices=['enable', 'disable'],
                             help="Choose whether you want to enable or disable an autoscan of a path")
scan_parser.add_argument("path", help="Where do you want to scan")
index_parser.add_argument("path", help="Which ")
autoscan_parser.add_argument("path")
autoscan_parser.add_argument("time_interval", type=int)
args = parser.parse_args()


def main(command, type_of_action, path, time_interval=None):
    database = Database(read_config_paths())
    if command == "scan":
        if type_of_action == 'full':
            (list_of_inf_files, dict_of_updated_files) = full_scan(path, database)
            if list_of_inf_files == []:
                print("No viruses found.")
            else:
                word = "viruses"
                if len(list_of_inf_files) == 1:
                    word = "virus"
                print(f"Found {word} in:")
                for inf_file in list_of_inf_files:
                    print(inf_file)
            write_dict_to_index(path, database, dict_of_updated_files)
        elif type_of_action == 'quick':
            (list_of_inf_files, dict_of_updated_files) = quick_scan(path, database)
            if list_of_inf_files == []:
                print("No viruses found.")
            else:
                word = "viruses"
                if len(list_of_inf_files) == 1:
                    word = "virus"
                print(f"Found {word} in:")
                for inf_file in list_of_inf_files:
                    print(inf_file)
            write_dict_to_index(path, database, dict_of_updated_files)
    elif command == "index":
        if type_of_action == 'create':
            create_index(path, database)
        elif type_of_action == 'update':
            update_index(path, database)
    elif command == "autoscan":
        if type_of_action == 'enable':
            enable_autoscan(path, time_interval)
        elif type_of_action == 'disable':
            disable_autoscan(path)


if __name__ == "__main__":
    if "type_of_scan" in args:
        main("scan", args.type_of_scan, args.path)
    elif "type_of_index_operation" in args:
        main("index", args.type_of_index_operation, args.path)
    elif "type_of_action" in args:
        main("autoscan", args.type_of_action, args.path, args.time_interval)
