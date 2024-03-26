#!/usr/bin/ python3
# @File    : job_service.py
# @Time    : 2022/5/13 14:50
# @Author  : Kelvin.Ye
from apscheduler.jobstores.base import JobLookupError
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.util import convert_to_datetime
from flask import request
from loguru import logger
from tzlocal import get_localzone

from app.database import db_query
from app.extension import apscheduler
from app.modules.schedule.dao import schedule_job_dao
from app.modules.schedule.enum import JobEvents
from app.modules.schedule.enum import JobState
from app.modules.schedule.enum import JobType
from app.modules.schedule.enum import TriggerType
from app.modules.schedule.model import TScheduleJob
from app.modules.schedule.model import TScheduleLog
from app.modules.schedule.service.job_function import jobfx
from app.modules.script.dao import element_children_dao
from app.modules.script.dao import test_element_dao
from app.modules.script.dao import testplan_dao
from app.modules.usercenter.model import TUser
from app.tools.exceptions import ServiceError
from app.tools.identity import new_id
from app.tools.localvars import get_trace_id
from app.tools.localvars import get_user_no
from app.tools.service import http_service
from app.tools.validator import check_exists
from app.tools.validator import check_not_exists
from app.tools.validator import check_workspace_permission
from app.utils.sqlalchemy_util import QueryCondition
from app.utils.time_util import TIMEFMT
from app.utils.time_util import datetime_now_by_utc8


@http_service
def query_job_list(req):
    # 查询条件
    conds = QueryCondition()
    conds.like(TScheduleJob.WORKSPACE_NO, req.workspaceNo)
    conds.like(TScheduleJob.JOB_NO, req.jobNo)
    conds.like(TScheduleJob.JOB_NAME, req.jobName)
    conds.like(TScheduleJob.JOB_DESC, req.jobDesc)
    conds.like(TScheduleJob.JOB_TYPE, req.jobType)
    conds.like(TScheduleJob.JOB_STATE, req.jobState)
    conds.like(TScheduleJob.TRIGGER_TYPE, req.triggerType)

    # 查询定时任务列表
    pagination = (
        TScheduleJob
        .filter(*conds)
        .order_by(TScheduleJob.CREATED_TIME.desc())
        .paginate(page=req.page, per_page=req.pageSize, error_out=False)
    )

    data = []
    for job in pagination.items:
        apjob = None
        if job.JOB_STATE != JobState.CLOSED.value:
            apjob = apscheduler.get_job(job.JOB_NO)
        data.append({
            'jobNo': job.JOB_NO,
            'jobName': job.JOB_NAME,
            'jobDesc': job.JOB_DESC,
            'jobType': job.JOB_TYPE,
            'jobArgs': get_job_args(job.JOB_TYPE, job.JOB_ARGS),
            'jobState': job.JOB_STATE,
            'triggerType': job.TRIGGER_TYPE,
            'createdTime': job.CREATED_TIME.strftime(TIMEFMT),
            'nextRunTime': apjob.next_run_time.strftime(TIMEFMT) if apjob else None,
        })

    return {'list': data, 'total': pagination.total}


def get_job_args(job_type, job_args):
    if job_type == JobType.TESTPLAN.value:
        testplan = testplan_dao.select_by_no(job_args['plan_no'])
        return {'name': testplan.PLAN_NAME}
    elif job_type == JobType.COLLECTION.value:
        collection = test_element_dao.select_by_no(job_args['collection_no'])
        return {'name': collection.ELEMENT_NAME}
    else:
        node = element_children_dao.select_by_child(job_args['worker_no'])
        testcase = test_element_dao.select_by_no(job_args['worker_no'])
        collection = test_element_dao.select_by_no(node.ROOT_NO)
        return {'name': f'/{collection.ELEMENT_NAME}/{testcase.ELEMENT_NAME}'}


@http_service
def query_job_info(req):
    # 查询定时任务
    job = schedule_job_dao.select_by_no(req.jobNo)
    check_exists(job, error='任务不存在')

    return {
        'jobNo': job.JOB_NO,
        'jobName': job.JOB_NAME,
        'jobDesc': job.JOB_DESC,
        'jobType': job.JOB_TYPE,
        'jobArgs': job.JOB_ARGS,
        'jobState': job.JOB_STATE,
        'triggerType': job.TRIGGER_TYPE,
        'triggerArgs': job.TRIGGER_ARGS
    }


@http_service
def create_job(req):
    # 校验空间权限
    check_workspace_permission(req.workspaceNo)

    # 唯一性校验
    if req.jobType == JobType.TESTPLAN.value:
        job = TScheduleJob.filter(
            TScheduleJob.WORKSPACE_NO == req.workspaceNo,
            TScheduleJob.JOB_ARGS['plan_no'].as_string() == req.jobArgs['plan_no'],
            TScheduleJob.JOB_STATE != JobState.CLOSED.value
        ).first()
    elif req.jobType == JobType.COLLECTION.value:
        job = TScheduleJob.filter(
            TScheduleJob.WORKSPACE_NO == req.workspaceNo,
            TScheduleJob.JOB_ARGS['collection_no'].as_string() == req.jobArgs['collection_no'],
            TScheduleJob.JOB_STATE != JobState.CLOSED.value
        ).first()
    else:
        job = TScheduleJob.filter(
            TScheduleJob.WORKSPACE_NO == req.workspaceNo,
            TScheduleJob.JOB_ARGS['worker_no'].as_string() == req.jobArgs['worker_no'],
            TScheduleJob.JOB_STATE != JobState.CLOSED.value
        ).first()
    check_not_exists(job, error='相同类型的任务已存在')

    # 添加作业
    job_no = new_id()
    # 新增定时任务
    TScheduleJob.insert(
        WORKSPACE_NO=req.workspaceNo,
        JOB_NO=job_no,
        JOB_NAME=req.jobName,
        JOB_DESC=req.jobDesc,
        JOB_TYPE=req.jobType,
        JOB_ARGS=req.jobArgs,
        TRIGGER_TYPE=req.triggerType,
        TRIGGER_ARGS=req.triggerArgs
    )

    # 新增历史记录
    TScheduleLog.insert(
        LOG_NO=get_trace_id(),
        JOB_NO=job_no,
        JOB_EVENT=JobEvents.ADD.value,
        OPERATION_BY=get_user_no(),
        OPERATION_TIME=datetime_now_by_utc8()
    )

    # 添加apscheduler作业
    if req.triggerType == TriggerType.DATE.value:
        apscheduler.add_job(
            id=job_no,
            name=req.jobName,
            func=jobfx.get(req.jobType),
            kwargs=req.jobArgs,
            trigger=DateTrigger(**req.triggerArgs) # args={'run_date': 'xxx'}
        )
    else:
        cron_trigger = CronTrigger.from_crontab(req.triggerArgs['crontab'])
        start_date = req.triggerArgs.get('start_date')
        end_date = req.triggerArgs.get('end_date')
        tz = get_localzone()
        if start_date:
            cron_trigger.start_date = convert_to_datetime(start_date, tz, 'start_date')
        if end_date:
            cron_trigger.end_date = convert_to_datetime(end_date, tz, 'end_date')
        apscheduler.add_job(
            id=job_no,
            name=req.jobName,
            func=jobfx.get(req.jobType),
            kwargs=req.jobArgs,
            trigger=cron_trigger # args={'crontab': 'xxx', 'start_date': 'xxx', 'end_date': 'xxx'}
        )

    return {'jobNo': job_no}


@http_service
def modify_job(req):
    # 校验空间权限
    check_workspace_permission(request.headers.get('x-workspace-no'))

    # 查询定时任务
    job = schedule_job_dao.select_by_no(req.jobNo)
    check_exists(job, error='任务不存在')

    if job.JOB_STATE != JobState.PENDING.value:
        raise ServiceError('任务已开始，不允许修改')

    # 唯一性校验
    if req.jobType == JobType.TESTPLAN.value:
        existing_job = TScheduleJob.filter(
            TScheduleJob.ID != job.ID,
            TScheduleJob.WORKSPACE_NO == req.workspaceNo,
            TScheduleJob.JOB_ARGS['plan_no'].as_string() == req.jobArgs['plan_no'],
            TScheduleJob.JOB_STATE != JobState.CLOSED.value
        ).first()
    elif req.jobType == JobType.COLLECTION.value:
        existing_job = TScheduleJob.filter(
            TScheduleJob.ID != job.ID,
            TScheduleJob.WORKSPACE_NO == req.workspaceNo,
            TScheduleJob.JOB_ARGS['collection_no'].as_string() == req.jobArgs['collection_no'],
            TScheduleJob.JOB_STATE != JobState.CLOSED.value
        ).first()
    else:
        existing_job = TScheduleJob.filter(
            TScheduleJob.ID != job.ID,
            TScheduleJob.WORKSPACE_NO == req.workspaceNo,
            TScheduleJob.JOB_ARGS['worker_no'].as_string() == req.jobArgs['worker_no'],
            TScheduleJob.JOB_STATE != JobState.CLOSED.value
        ).first()
    check_not_exists(existing_job, error='相同内容的任务已存在')

    # 更新作业信息
    job.update(
        JOB_NAME=req.jobName,
        JOB_DESC=req.jobDesc,
        JOB_ARGS=req.jobArgs,
        TRIGGER_TYPE=req.triggerType,
        TRIGGER_ARGS=req.triggerArgs
    )

    # 更新作业
    if req.triggerType == TriggerType.DATE.value:
        apscheduler.modify_job(
            id=job.JOB_NO,
            name=req.jobName,
            kwargs=req.jobArgs,
            trigger=DateTrigger(**req.triggerArgs)
        )
    else:
        cron_trigger = CronTrigger.from_crontab(req.triggerArgs['crontab'])
        start_date = req.triggerArgs.get('start_date')
        end_date = req.triggerArgs.get('end_date')
        tz = get_localzone()
        if start_date:
            cron_trigger.start_date = convert_to_datetime(start_date, tz, 'start_date')
        if end_date:
            cron_trigger.end_date = convert_to_datetime(end_date, tz, 'end_date')
        apscheduler.modify_job(
            id=job.JOB_NO,
            name=req.jobName,
            kwargs=req.jobArgs,
            trigger=cron_trigger
        )


@http_service
def pause_job(req):
    # 校验空间权限
    check_workspace_permission(request.headers.get('x-workspace-no'))
    # 查询定时任务
    job = schedule_job_dao.select_by_no(req.jobNo)
    check_exists(job, error='任务不存在')
    # 更新作业状态
    job.update(JOB_STATE=JobState.PAUSED.value)
    # 新增历史记录
    TScheduleLog.insert(
        LOG_NO=get_trace_id(),
        JOB_NO=job.JOB_NO,
        JOB_EVENT=JobEvents.PAUSE.value,
        OPERATION_BY=get_user_no(),
        OPERATION_TIME=datetime_now_by_utc8()
    )
    # 暂停作业
    apscheduler.get_job(job.JOB_NO).pause()


@http_service
def resume_job(req):
    # 校验空间权限
    check_workspace_permission(request.headers.get('x-workspace-no'))
    # 查询定时任务
    job = schedule_job_dao.select_by_no(req.jobNo)
    check_exists(job, error='任务不存在')
    # 更新作业状态
    job.update(JOB_STATE=JobState.NORMAL.value)
    # 新增历史记录
    TScheduleLog.insert(
        LOG_NO=get_trace_id(),
        JOB_NO=job.JOB_NO,
        JOB_EVENT=JobEvents.RESUME.value,
        OPERATION_BY=get_user_no(),
        OPERATION_TIME=datetime_now_by_utc8()
    )
    # 恢复作业
    apscheduler.get_job(job.JOB_NO).resume()


@http_service
def remove_job(req):
    # 校验空间权限
    check_workspace_permission(request.headers.get('x-workspace-no'))

    # 查询定时任务
    job = schedule_job_dao.select_by_no(req.jobNo)
    check_exists(job, error='任务不存在')

    # 更新状态
    job.JOB_STATE != JobState.CLOSED.value and job.update(JOB_STATE=JobState.CLOSED.value)

    # 移除作业
    try:
        apscheduler.remove_job(job.JOB_NO)
    except JobLookupError:
        logger.info(f'jobNo:[{job.JOB_NO}] 作业不存在或已失效')


@http_service
def query_job_log_list(req):
    # 查询条件
    conds = QueryCondition(TScheduleJob, TScheduleLog)
    conds.equal(TScheduleJob.WORKSPACE_NO, req.workspaceNo)
    conds.equal(TScheduleJob.JOB_NO, req.jobNo)
    conds.like(TScheduleJob.JOB_NAME, req.jobName)
    conds.equal(TScheduleLog.LOG_NO, req.logNo)
    conds.equal(TScheduleLog.JOB_EVENT, req.jobEvent)
    conds.ge(TScheduleLog.CREATED_TIME, req.startTime)
    conds.le(TScheduleLog.CREATED_TIME, req.endTime)
    conds.equal(TScheduleJob.JOB_NO, TScheduleLog.JOB_NO)

    # 查询日志列表
    pagination = (
        db_query(
            TScheduleLog.LOG_NO,
            TScheduleJob.JOB_NO,
            TScheduleJob.JOB_NAME,
            TScheduleJob.JOB_TYPE,
            TScheduleJob.JOB_ARGS,
            TScheduleLog.JOB_EVENT,
            TScheduleLog.OPERATION_TIME,
            TUser.USER_NAME
        )
        .outerjoin(TUser, TScheduleLog.OPERATION_BY == TUser.USER_NO)
        .filter(*conds)
        .order_by(TScheduleLog.CREATED_TIME.desc())
        .paginate(page=req.page, per_page=req.pageSize, error_out=False)
    )

    data = [
        {
            'logNo': item.LOG_NO,
            'jobNo': item.JOB_NO,
            'jobName': item.JOB_NAME,
            'jobType': item.JOB_TYPE,
            'jobArgs': get_job_args(item.JOB_TYPE, item.JOB_ARGS),
            'jobEvent': item.JOB_EVENT,
            'operationBy': item.USER_NAME,
            'operationTime': item.OPERATION_TIME.strftime(TIMEFMT)
        }
        for item in pagination.items
    ]

    return {'list': data, 'total': pagination.total}
