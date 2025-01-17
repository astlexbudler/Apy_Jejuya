from apscheduler.schedulers.background import BackgroundScheduler
from . import models



def startScheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(clean_security_tables, 'interval', minutes=10)
    scheduler.start()

def clean_security_tables(): # clean security tables
    models.ACCESS_IP.objects.all().delete()
    return