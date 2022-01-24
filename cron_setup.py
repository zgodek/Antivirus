from crontab import CronTab
import os


def enable_autoscan(path, how_many_minutes):
    """
    sets a regular quick scan of a given path as a cron job in given time intervals
    """
    cron = CronTab(user=True)
    folder = os.path.dirname(__file__)
    job = cron.new(command=f"python3 {folder}/main.py 'quick scan' '{path}'", comment=path+"_"+str(how_many_minutes))
    job.minute.every(how_many_minutes)
    cron.write()


def disable_autoscan(path, how_many_minutes):
    """
    removes regular quick scan cron job for a given path
    """
    cron = CronTab(user=True)
    for job in cron:
        if job.comment == path+"_"+str(how_many_minutes):
            cron.remove(job)
    cron.write()
