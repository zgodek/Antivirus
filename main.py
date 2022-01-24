from database import Database
from scan import full_scan, quick_scan
from index import create_index, update_index, write_dict_to_index
from cron_setup import set_up_cron, disable_cron
import argparse
import json
import os


class WrongActionError(Exception):
    def __init__(self, message):
        super().__init__(message)


def read_config_paths():
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
parser.add_argument('action', type=str, help="What type of action do you" +
                    " want to perform: 'full scan', 'quick scan'," +
                    " 'create index', 'update index', 'enable autoscan', 'disable autoscan'")
parser.add_argument('path', type=str, nargs='?', help="Where do you want" +
                    " to perform chosen action")
parser.add_argument('time_interval', type=int, nargs='?', help="In what time" +
                    " intervals (in minutes) do you want to perform quick" +
                    " scan in chosen path")
args = parser.parse_args()


def main(action, path, time_interval=None):
    database = Database(read_config_paths())
    if action == 'full scan':
        (list_of_inf_files, dict_of_updated_files) = full_scan(path, database)
        if list_of_inf_files == []:
            print("No viruses found.")
        else:
            word = "viruses"
            if len(list_of_inf_files) == 1:
                word = "virus"
            print(f"Found {word}:")
            for inf_file in list_of_inf_files:
                print(inf_file)
        write_dict_to_index(path, database, dict_of_updated_files)
    elif action == 'quick scan':
        (list_of_inf_files, dict_of_updated_files) = quick_scan(path, database)
        if list_of_inf_files == []:
            print("No viruses found.")
        else:
            word = "viruses"
            if len(list_of_inf_files) == 1:
                word = "virus"
            print(f"Found {word}:")
            for inf_file in list_of_inf_files:
                print(inf_file)
        write_dict_to_index(path, database, dict_of_updated_files)
    elif action == 'create index':
        create_index(path, database)
    elif action == 'update index':
        update_index(path, database)
    elif action == 'enable autoscan':
        set_up_cron(path, time_interval)
    elif action == 'disable autoscan':
        disable_cron(path)
    else:
        raise WrongActionError("The action you have chosen does not exist.")


if __name__ == "__main__":
    main(args.action, args.path, args.time_interval)
