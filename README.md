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
Virus hashes have to be seperated by a newline, but they can be in one file or in multiple.

Then you have to create a directory for index files.

After creating those 3 directories, which can be located anywhere in the system (but one cannot contain another!), you have to enter their paths to config_database.json file.

All of the instructions regarding actual usage of the antivirus can be found in python3 main.py --help.
