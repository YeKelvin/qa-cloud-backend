#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : event.py
# @Time    : 2022-05-15 23:34:10
# @Author  : Kelvin.Ye
from apscheduler.events import JobEvent
from apscheduler.events import JobExecutionEvent
from apscheduler.events import JobSubmissionEvent
from apscheduler.events import SchedulerEvent

from app.extension import apscheduler
from app.extension import db
from app.schedule.dao import schedule_job_dao as ScheduleJobDao
from app.schedule.enum import JobState
from app.utils.log_util import get_logger
from app.utils.time_util import datetime_now_by_utc8


log = get_logger(__name__)


def handle_scheduler_started(event: SchedulerEvent):
    """
    EVENT_SCHEDULER_STARTED
    The scheduler was started
    """
    log.info('event:[ EVENT_SCHEDULER_STARTED ] the scheduler was started')


def handle_scheduler_shutdown(event: SchedulerEvent):
    """
    EVENT_SCHEDULER_SHUTDOWN
    The scheduler was shutdown
    """
    log.info('event:[ EVENT_SCHEDULER_SHUTDOWN ] the scheduler was shutdown')


def handle_scheduler_paused(event: SchedulerEvent):
    """
    EVENT_SCHEDULER_PAUSED
    Job processing in the scheduler was paused
    """
    log.info('event:[ EVENT_SCHEDULER_PAUSED ] job processing in the scheduler was paused')


def handle_scheduler_resumed(event: SchedulerEvent):
    """
    EVENT_SCHEDULER_RESUMED
    Job processing in the scheduler was resumed
    """
    log.info('event:[ EVENT_SCHEDULER_RESUMED ] job processing in the scheduler was resumed')


def handle_executor_added(event: SchedulerEvent):
    """
    EVENT_EXECUTOR_ADDED
    An executor was added to the scheduler
    """
    ...


def handle_executor_removed(event: SchedulerEvent):
    """
    EVENT_EXECUTOR_REMOVED
    An executor was removed to the scheduler
    """
    ...


def handle_jobstore_added(event: SchedulerEvent):
    """
    EVENT_JOBSTORE_ADDED
    A job store was added to the scheduler
    """
    ...


def handle_jobstore_removed(event: SchedulerEvent):
    """
    EVENT_JOBSTORE_REMOVED
    A job store was removed from the scheduler
    """
    ...


def handle_all_jobs_removed(event: SchedulerEvent):
    """
    EVENT_ALL_JOBS_REMOVED
    All jobs were removed from either all job stores or one particular job store
    """
    log.info(
        'event:[ EVENT_ALL_JOBS_REMOVED ] all jobs were removed from either all job stores or one particular job store'
    )


def handle_job_added(event: JobEvent):
    """
    EVENT_JOB_ADDED
    A job was added to a job store
    """
    log.info(f'event:[ EVENT_JOB_ADDED ] jobId:[ {event.job_id} ] 添加作业')


def handle_job_removed(event: JobEvent):
    """
    EVENT_JOB_REMOVED
    A job was removed from a job store
    """
    log.info(f'event:[ EVENT_JOB_REMOVED ] jobId:[ {event.job_id} ] 移除作业')
    # 更新任务状态
    with apscheduler.app.app_context():
        task = ScheduleJobDao.select_by_no(event.job_id)
        if task and task.STATE != JobState.CLOSED.value:
            log.info(f'jobId:[ {event.job_id} ] 更新任务状态为CLOSED')
            task.update(
                STATE=JobState.CLOSED.value,
                CLOSE_BY='system',
                CLOSE_TIME=datetime_now_by_utc8()
            )
            db.session.commit()


def handle_job_modified(event: JobEvent):
    """
    EVENT_JOB_MODIFIED
    A job was modified from outside the scheduler
    """
    log.info(f'event:[ EVENT_JOB_MODIFIED ] jobId:[ {event.job_id} ] 修改作业')


def handle_job_submitted(event: JobSubmissionEvent):
    """
    EVENT_JOB_SUBMITTED
    A job was submitted to its executor to be run
    """
    log.info(f'event:[ EVENT_JOB_SUBMITTED ] jobId:[ {event.job_id} ] 提交作业')


def handle_job_max_instances(event: JobSubmissionEvent):
    """
    EVENT_JOB_MAX_INSTANCES
    A job being submitted to its executor was not accepted by the executor because the job has already reached its maximum concurrently executing instances
    """
    log.warning(f'event:[ EVENT_JOB_MAX_INSTANCES ] jobId:[ {event.job_id} ] 已达到最大并发执行实例数，作业提交失败')


def handle_job_executed(event: JobExecutionEvent):
    """
    EVENT_JOB_EXECUTED
    A job was executed successfully
    """
    log.info(f'event:[ EVENT_JOB_EXECUTED ] jobId:[ {event.job_id} ] 执行作业')


def handle_job_error(event: JobExecutionEvent):
    """
    EVENT_JOB_ERROR
    A job raised an exception during execution
    """
    log.error(f'event:[ EVENT_JOB_ERROR ] jobId:[ {event.job_id} ] 作业异常:\n{event.traceback.format_exc()}')


def handle_job_missed(event: JobExecutionEvent):
    """
    EVENT_JOB_MISSED
    A job’s execution was missed
    """
    ...


def handle_event_all():
    """
    EVENT_ALL
    A catch-all mask that includes every event type
    """
    ...
