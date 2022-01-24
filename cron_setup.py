from crontab import CronTab
import os


def set_up_cron(path, how_many_minutes):
    cron = CronTab(user=True)
    folder = os.path.dirname(__file__)
    job = cron.new(command=f"python3 {folder}/main.py 'quick scan' '{path}'", comment=path)
    job.minute.every(how_many_minutes)
    cron.write()


def disable_cron(path):
    cron = CronTab(user=True)
    for job in cron:
        if job.comment == path:
            cron.remove(job)
    cron.write()
