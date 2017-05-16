import datetime

import pytz
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.util import undefined

from micronurse import settings

scheduler = None


def init_scheduler():
    global scheduler
    jobstores = {
        'default': RedisJobStore(db=settings.MICRONURSE_SCHEDULER['REDIS_DB'])
    }
    executors = {
        'default': ThreadPoolExecutor(settings.MICRONURSE_SCHEDULER['THREAD_POOL_SIZE']),
        'processpool': ProcessPoolExecutor(5)
    }
    job_defaults = {
        'coalesce': False,
        'max_instances': settings.MICRONURSE_SCHEDULER['MAX_JOB_INSTANCE']
    }
    scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults,
                                    timezone=pytz.timezone(settings.TIME_ZONE))
    scheduler.start()
    print('Scheduler is running...')


def stop_scheduler():
    global scheduler
    scheduler.shutdown(wait=False)
    print('Scheduler has stopped.')


def add_interval_job(job_id: str, job_func, minutes: int, start_time: datetime=undefined, args: list=None):
    scheduler.add_job(job_func, trigger='interval', minutes=int(minutes),
                      id=str(job_id), replace_existing=True, args=args,
                      next_run_time=start_time)
