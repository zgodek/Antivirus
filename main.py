from database import Database
from scan import full_scan, quick_scan
from index import create_index, update_index, write_dict_to_index
import argparse


database = Database()

parser = argparse.ArgumentParser(description='Perform a full scan, a quick scan, create an index of a folder or update an index of a folder')
parser.add_argument('action', type=str, help='What type of action do you want to perform')
parser.add_argument('path', type=str, help='Where do you want to perform chosen action')
args = parser.parse_args()


def main(action, path):
    if action == 'full scan':
        full_scan_result = full_scan(path, database)
        print(full_scan_result[0])
        write_dict_to_index(path, database, full_scan_result[1])
    if action == 'quick scan':
        quick_scan_result = quick_scan(path, database)
        print(quick_scan_result[0])
        write_dict_to_index(path, database, quick_scan_result[1])
    if action == 'create index':
        create_index(path, database)
    if action == 'update index':
        update_index(path, database)
    return


if __name__ == "__main__":
    main(args.action, args.path)
