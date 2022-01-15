#!/usr/bin/python
from database import Database
from scan import full_scan, quick_scan
from index import save_index_to_json, update_index_in_json
import sys
import argparse


database = Database()

parser = argparse.ArgumentParser(description='Perform a full scan, a quick scan, create an index of a folder or update an index')
parser.add_argument('action', type=str, help='What type of action do you want to perform')
parser.add_argument('path', type=str, help='Where do you want to perform chosen action')
parser.add_argument('create index', type=str, help='Of which folder do you want to create an index')
parser.add_argument('update index', type=str, help='Which folders index do you want to update')
args = parser.parse_args()


def main(action, path):
    if action == 'full scan':
        full_scan(path, database)
    if action == 'quick scan':
        quick_scan(path, database)
    if action == 'create index':
        save_index_to_json(path, database)
    if action == 'update index':
        update_index_in_json(path, database)
    return


if __name__ == "__main__":
    main(args.action, args.path)
