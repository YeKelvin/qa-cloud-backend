#!/usr/bin/ python3
# @File    : event.py
# @Time    : 2022-05-15 23:34:10
# @Author  : Kelvin.Ye
from apscheduler.events import JobEvent
from apscheduler.events import JobExecutionEvent
from apscheduler.events import JobSubmissionEvent
from apscheduler.events import SchedulerEvent
from loguru import logger

from app.extension import db
from app.modules.schedule.dao import schedule_job_dao
from app.modules.schedule.decorator import apscheduler_app_context
from app.modules.schedule.enum import JobEvents
from app.modules.schedule.enum import JobState
from app.modules.schedule.model import TScheduleLog
from app.tools.identity import new_ulid
from app.tools.localvars import traceid_var
from app.utils.time_util import datetime_now_by_utc8


def handle_scheduler_started(event: SchedulerEvent):
    """EVENT_SCHEDULER_STARTED

    The scheduler was started
    """
    logger.info('event:[ EVENT_SCHEDULER_STARTED ] the scheduler was started')


def handle_scheduler_shutdown(event: SchedulerEvent):
    """EVENT_SCHEDULER_SHUTDOWN

    The scheduler was shutdown
    """
    logger.info('event:[ EVENT_SCHEDULER_SHUTDOWN ] the scheduler was shutdown')


def handle_scheduler_paused(event: SchedulerEvent):
    """EVENT_SCHEDULER_PAUSED

    Job processing in the scheduler was paused
    """
    logger.info('event:[ EVENT_SCHEDULER_PAUSED ] job processing in the scheduler was paused')


def handle_scheduler_resumed(event: SchedulerEvent):
    """EVENT_SCHEDULER_RESUMED

    Job processing in the scheduler was resumed
    """
    logger.info('event:[ EVENT_SCHEDULER_RESUMED ] job processing in the scheduler was resumed')


def handle_executor_added(event: SchedulerEvent):
    """EVENT_EXECUTOR_ADDED

    An executor was added to the scheduler
    """
    pass


def handle_executor_removed(event: SchedulerEvent):
    """EVENT_EXECUTOR_REMOVED

    An executor was removed to the scheduler
    """
    pass


def handle_jobstore_added(event: SchedulerEvent):
    """EVENT_JOBSTORE_ADDED

    A job store was added to the scheduler
    """
    pass


def handle_jobstore_removed(event: SchedulerEvent):
    """EVENT_JOBSTORE_REMOVED

    A job store was removed from the scheduler
    """
    pass


def handle_all_jobs_removed(event: SchedulerEvent):
    """EVENT_ALL_JOBS_REMOVED

    All jobs were removed from either all job stores or one particular job store
    """
    logger.info(
        'event:[ EVENT_ALL_JOBS_REMOVED ] all jobs were removed from either all job stores or one particular job store'
    )


def handle_job_added(event: JobEvent):
    """EVENT_JOB_ADDED

    A job was added to a job store
    """
    logger.info(f'event:[ EVENT_JOB_ADDED ] jobId:[ {event.job_id} ] 作业已添加')


@apscheduler_app_context
def handle_job_removed(event: JobEvent):
    """EVENT_JOB_REMOVED

    A job was removed from a job store
    """
    logger.info(f'event:[ EVENT_JOB_REMOVED ] jobId:[ {event.job_id} ] 作业已移除')
    # 更新任务状态
    try:
        # 查询任务
        job = schedule_job_dao.select_by_no(event.job_id)
        if not job:
            return
        # 如果任务状态仍未关闭，则更新状态为已关闭
        if job.JOB_STATE != JobState.CLOSED.value:
            logger.info(f'jobId:[ {event.job_id} ] 更新任务状态为CLOSED')
            job.update(STATE=JobState.CLOSED.value)
        # 新增历史记录
        TScheduleLog.insert(
            LOG_NO=traceid_var.get() or new_ulid(),
            JOB_NO=job.JOB_NO,
            JOB_EVENT=JobEvents.CLOSE.value,
            OPERATION_BY='9999',
            OPERATION_TIME=datetime_now_by_utc8()
        )
        # 需要手动提交
        db.session.commit()
    except Exception:
        # 数据回滚
        db.session.rollback()
        logger.exception('Exception Occurred')


def handle_job_modified(event: JobEvent):
    """EVENT_JOB_MODIFIED

    A job was modified from outside the scheduler
    """
    logger.info(f'event:[ EVENT_JOB_MODIFIED ] jobId:[ {event.job_id} ] 作业已修改')


@apscheduler_app_context
def handle_job_submitted(event: JobSubmissionEvent):
    """EVENT_JOB_SUBMITTED

    A job was submitted to its executor to be run
    """
    logger.info(f'event:[ EVENT_JOB_SUBMITTED ] jobId:[ {event.job_id} ] 开始执行作业')
    try:
        # 查询任务
        job = schedule_job_dao.select_by_no(event.job_id)
        if not job:
            return
        # 更新状态
        job.JOB_STATE != JobState.PENDING.value and job.update(JOB_STATE=JobState.RUNNING.value)
        # 新增历史记录
        TScheduleLog.insert(
            LOG_NO=traceid_var.get() or new_ulid(),
            JOB_NO=job.JOB_NO,
            JOB_EVENT=JobEvents.EXECUTE.value,
            OPERATION_BY='9999',
            OPERATION_TIME=datetime_now_by_utc8()
        )
        # 需要手动提交
        db.session.commit()
    except Exception:
        # 数据回滚
        db.session.rollback()
        logger.exception('Exception Occurred')


def handle_job_max_instances(event: JobSubmissionEvent):
    """EVENT_JOB_MAX_INSTANCES

    A job being submitted to its executor was not accepted by the executor,
    because the job has already reached its maximum concurrently executing instances
    """
    logger.warning(f'event:[ EVENT_JOB_MAX_INSTANCES ] jobId:[ {event.job_id} ] 已达到最大并发执行实例数，作业提交失败')


def handle_job_executed(event: JobExecutionEvent):
    """EVENT_JOB_EXECUTED

    A job was executed successfully
    """
    logger.info(f'event:[ EVENT_JOB_EXECUTED ] jobId:[ {event.job_id} ] 作业执行完成')


def handle_job_error(event: JobExecutionEvent):
    """EVENT_JOB_ERROR

    A job raised an exception during execution
    """
    logger.exception(f'event:[ EVENT_JOB_ERROR ] jobId:[ {event.job_id} ] 作业执行异常')


def handle_job_missed(event: JobExecutionEvent):
    """EVENT_JOB_MISSED

    A job’s execution was missed
    """
    pass


def handle_event_all(event):
    """EVENT_ALL

    A catch-all mask that includes every event type
    """
    # 设置[ 线程/协程 ]的日志号
    traceid_var.set(new_ulid())
