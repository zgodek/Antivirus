# Antivirus

You need to have these python libraries installed:
python-crontab

The rest is in the Python Standard Library.

To run this program properly you need to have listed files in one folder:
file.py
database.py
index.py
scan.py
main.py
cron_setup.py
config_database.json

You also need to have 2 different and seperate folders, one for virus hashes and one for virus sequences.
In virus sequences folder each virus sequence has to be in a seperate file.
Virus hashes have to be seperated by a newline, but they can be in a one file or in multiple, but all of those files have to be in the virus hashes folder.

After creating those 3 different directories you have to enter their paths to config_database.json.
All of the instructions regarding actual usage of the antivirus can be found in python3 main.py --help.
