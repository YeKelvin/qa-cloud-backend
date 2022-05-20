#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : task_service.py
# @Time    : 2022/5/13 14:50
# @Author  : Kelvin.Ye
from apscheduler.jobstores.base import JobLookupError
from apscheduler.triggers.cron import CronTrigger

from app.common.decorators.service import http_service
from app.common.decorators.transaction import transactional
from app.common.globals import get_userno
from app.common.identity import new_id
from app.common.validator import check_exists
from app.common.validator import check_not_exists
from app.common.validator import check_workspace_permission
from app.extension import apscheduler
from app.schedule.dao import schedule_job_dao as ScheduleJobDao
from app.schedule.enum import JobState
from app.schedule.enum import JobType
from app.schedule.enum import TriggerType
from app.schedule.model import TScheduleJob
from app.schedule.service.task_function import TASK_FUNC
from app.utils.log_util import get_logger
from app.utils.time_util import datetime_now_by_utc8


log = get_logger(__name__)


@http_service
def query_task_list(req):
    # 查询定时任务列表
    pagination = ScheduleJobDao.select_list(
        workspaceNo=req.workspaceNo,
        jobNo=req.jobNo,
        jobName=req.jobName,
        jobDesc=req.jobDesc,
        jobType=req.jobType,
        triggerType=req.triggerType,
        state=req.state,
        page=req.page,
        pageSize=req.pageSize
    )

    data = []
    for task in pagination.items:
        data.append({
            'jobNo': task.JOB_NO,
            'jobName': task.JOB_NAME,
            'jobDesc': task.JOB_DESC,
            'jobType': task.JOB_TYPE,
            'triggerType': task.TRIGGER_TYPE,
            'state': task.STATE,
            'pauseBy': task.PAUSE_BY,
            'pauseTime': task.PAUSE_TIME,
            'resumeBy': task.RESUME_BY,
            'resumeTime': task.RESUME_TIME,
            'closeBy': task.CLOSE_BY,
            'closeTime': task.CLOSE_TIME
        })

    return {'data': data, 'total': pagination.total}


@http_service
def query_task_info(req):
    # 查询定时任务
    task = ScheduleJobDao.select_by_no(req.jobNo)
    check_exists(task, '任务不存在')

    return {
        'jobNo': task.JOB_NO,
        'jobName': task.JOB_NAME,
        'jobDesc': task.JOB_DESC,
        'jobType': task.JOB_TYPE,
        'jobArgs': task.JOB_ARGS,
        'triggerType': task.TRIGGER_TYPE,
        'triggerArgs': task.TRIGGER_ARGS,
        'state': task.STATE,
        'pauseBy': task.PAUSE_BY,
        'pauseTime': task.PAUSE_TIME,
        'resumeBy': task.RESUME_BY,
        'resumeTime': task.RESUME_TIME,
        'closeBy': task.CLOSE_BY,
        'closeTime': task.CLOSE_TIME
    }


@http_service
@transactional
def create_task(req):
    # 校验空间权限
    check_workspace_permission(req.workspaceNo)

    # 唯一性校验
    if req.jobType == JobType.TESTPLAN.value:
        task = TScheduleJob.filter(
            TScheduleJob.WORKSPACE_NO == req.workspaceNo,
            TScheduleJob.JOB_ARGS['planNo'].as_string() == req.jobArgs['planNo'],
            TScheduleJob.STATE != JobState.CLOSED.value
        ).first()
    elif req.jobType == JobType.COLLECTION.value:
        task = TScheduleJob.filter(
            TScheduleJob.WORKSPACE_NO == req.workspaceNo,
            TScheduleJob.JOB_ARGS['collectionNo'].as_string() == req.jobArgs['collectionNo'],
            TScheduleJob.STATE != JobState.CLOSED.value
        ).first()
    else:
        task = TScheduleJob.filter(
            TScheduleJob.WORKSPACE_NO == req.workspaceNo,
            TScheduleJob.JOB_ARGS['groupNo'].as_string() == req.jobArgs['groupNo'],
            TScheduleJob.STATE != JobState.CLOSED.value
        ).first()
    check_not_exists(task, '相同内容的任务已存在')

    # 添加作业
    job_no = new_id()
    if req.triggerType == TriggerType.DATE.value:
        apscheduler.add_job(
            id=job_no,
            name=req.jobName,
            func=TASK_FUNC.get(req.jobType),
            kwargs=req.jobArgs,
            trigger=req.triggerType.lower(),
            run_date=req.triggerArgs['datetime']
        )
    elif req.triggerType == TriggerType.INTERVAL.value:
        apscheduler.add_job(
            id=job_no,
            name=req.jobName,
            func=TASK_FUNC.get(req.jobType),
            kwargs=req.jobArgs,
            trigger=req.triggerType.lower(),
            **req.triggerArgs
        )
    else:
        apscheduler.add_job(
            id=job_no,
            name=req.jobName,
            func=TASK_FUNC.get(req.jobType),
            kwargs=req.jobArgs,
            trigger=CronTrigger.from_crontab(req.triggerArgs['crontab'])
        )

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

    return {'jobNo': job_no}


@http_service
@transactional
def modify_task(req):
    # 查询定时任务
    task = ScheduleJobDao.select_by_no(req.jobNo)
    check_exists(task, '任务不存在')

    # 校验空间权限
    check_workspace_permission(task.WORKSPACE_NO)

    # 唯一性校验
    if req.jobType == JobType.TESTPLAN.value:
        existed_task = TScheduleJob.filter(
            TScheduleJob.ID != task.ID,
            TScheduleJob.WORKSPACE_NO == req.workspaceNo,
            TScheduleJob.JOB_ARGS['planNo'].as_string() == req.jobArgs['planNo'],
            TScheduleJob.STATE != JobState.CLOSED.value
        ).first()
    elif req.jobType == JobType.COLLECTION.value:
        existed_task = TScheduleJob.filter(
            TScheduleJob.ID != task.ID,
            TScheduleJob.WORKSPACE_NO == req.workspaceNo,
            TScheduleJob.JOB_ARGS['collectionNo'].as_string() == req.jobArgs['collectionNo'],
            TScheduleJob.STATE != JobState.CLOSED.value
        ).first()
    else:
        existed_task = TScheduleJob.filter(
            TScheduleJob.ID != task.ID,
            TScheduleJob.WORKSPACE_NO == req.workspaceNo,
            TScheduleJob.JOB_ARGS['groupNo'].as_string() == req.jobArgs['groupNo'],
            TScheduleJob.STATE != JobState.CLOSED.value
        ).first()
    check_not_exists(existed_task, '相同内容的任务已存在')

    # 更新作业
    if req.triggerType == TriggerType.DATE.value:
        apscheduler.modify_job(
            id=task.JOB_NO,
            name=req.jobName,
            kwargs=req.jobArgs,
            trigger=req.triggerType.lower(),
            run_date=req.triggerArgs['datetime']
        )
    elif req.triggerType == TriggerType.INTERVAL.value:
        apscheduler.modify_job(
            id=task.JOB_NO,
            name=req.jobName,
            kwargs=req.jobArgs,
            trigger=req.triggerType.lower(),
            **req.triggerArgs
        )
    else:
        apscheduler.modify_job(
            id=task.JOB_NO,
            name=req.jobName,
            kwargs=req.jobArgs,
            trigger=CronTrigger.from_crontab(req.triggerArgs['crontab'])
        )

    # 更新作业信息
    task.update(
        JOB_NAME=req.jobName,
        JOB_DESC=req.jobDesc,
        JOB_ARGS=req.jobArgs,
        TRIGGER_TYPE=req.triggerType,
        TRIGGER_ARGS=req.triggerArgs
    )


@http_service
@transactional
def pause_task(req):
    # 查询定时任务
    task = ScheduleJobDao.select_by_no(req.jobNo)
    check_exists(task, '任务不存在')

    # 校验空间权限
    check_workspace_permission(task.WORKSPACE_NO)

    # 暂停作业
    apscheduler.get_job(task.JOB_NO).pause()

    # 更新作业状态
    task.update(
        STATE=JobState.PAUSED.value,
        PAUSE_BY=get_userno(),
        PAUSE_TIME=datetime_now_by_utc8()
    )


@http_service
@transactional
def resume_task(req):
    # 查询定时任务
    task = ScheduleJobDao.select_by_no(req.jobNo)
    check_exists(task, '任务不存在')

    # 校验空间权限
    check_workspace_permission(task.WORKSPACE_NO)

    # 恢复作业
    apscheduler.get_job(task.JOB_NO).resume()

    # 更新作业状态
    task.update(
        STATE=JobState.NORMAL.value,
        RESUME_BY=get_userno(),
        RESUME_TIME=datetime_now_by_utc8()
    )


@http_service
@transactional
def remove_task(req):
    # 查询定时任务
    task = ScheduleJobDao.select_by_no(req.jobNo)
    check_exists(task, '任务不存在')

    # 校验空间权限
    check_workspace_permission(task.WORKSPACE_NO)

    # 移除作业
    try:
        apscheduler.remove_job(task.JOB_NO)
    except JobLookupError:
        log.info('查找作业失败，作业不存在或已失效')

    # 更新作业状态
    task = ScheduleJobDao.select_by_no(req.jobNo)
    if task and task.STATE != JobState.CLOSED.value:
        task.update(
            STATE=JobState.CLOSED.value,
            CLOSE_BY=get_userno(),
            CLOSE_TIME=datetime_now_by_utc8()
        )
