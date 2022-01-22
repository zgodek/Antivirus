from crontab import CronTab
from database import Database
import os


def set_up_cron(path, how_many_minutes):
    cron = CronTab(user=True)
    folder = os.path.dirname(__file__)
    job = cron.new(command=f"python3 {folder}/main.py 'quick scan' '{path}' >> /home/zgodek/antivirus.log 2>&1")
    job.minute.every(how_many_minutes)
    cron.write()


def disable_cron():
    cron = CronTab(user=True)
    cron.remove_all()
    cron.write()
