#!/usr/bin/ python3
# @File    : task_service.py
# @Time    : 2022/5/13 14:50
# @Author  : Kelvin.Ye
from apscheduler.jobstores.base import JobLookupError
from apscheduler.triggers.cron import CronTrigger
from loguru import logger

from app.database import dbquery
from app.extension import apscheduler
from app.modules.schedule.dao import schedule_job_dao

# from app.modules.schedule.enum import ChangeType
from app.modules.schedule.enum import JobState
from app.modules.schedule.enum import JobType
from app.modules.schedule.enum import OperationType
from app.modules.schedule.enum import TriggerType

# from app.modules.schedule.model import TScheduleJobChangeDetails
from app.modules.schedule.model import TScheduleJob
from app.modules.schedule.model import TScheduleJobLog
from app.modules.schedule.service.task_function import TASK_FUNC
from app.modules.usercenter.model import TUser
from app.tools.identity import new_id
from app.tools.localvars import get_user_no
from app.tools.service import http_service
from app.tools.validator import check_exists
from app.tools.validator import check_not_exists
from app.tools.validator import check_workspace_permission
from app.utils.json_util import to_json
from app.utils.sqlalchemy_util import QueryCondition
from app.utils.time_util import datetime_now_by_utc8


@http_service
def query_task_list(req):
    # 查询条件
    conds = QueryCondition()
    conds.like(TScheduleJob.WORKSPACE_NO, req.workspaceNo)
    conds.like(TScheduleJob.JOB_NO, req.jobNo)
    conds.like(TScheduleJob.JOB_NAME, req.jobName)
    conds.like(TScheduleJob.JOB_DESC, req.jobDesc)
    conds.like(TScheduleJob.JOB_TYPE, req.jobType)
    conds.like(TScheduleJob.TRIGGER_TYPE, req.triggerType)
    conds.like(TScheduleJob.STATE, req.state)

    # 查询定时任务列表
    pagination = (
        TScheduleJob
        .filter(*conds)
        .order_by(TScheduleJob.CREATED_TIME.desc())
        .paginate(page=req.page, per_page=req.pageSize, error_out=False)
    )

    data = [
        {
            'jobNo': task.JOB_NO,
            'jobName': task.JOB_NAME,
            'jobDesc': task.JOB_DESC,
            'jobType': task.JOB_TYPE,
            'triggerType': task.TRIGGER_TYPE,
            'state': task.STATE,
            'createdTime': task.CREATED_TIME
        }
        for task in pagination.items
    ]

    return {'data': data, 'total': pagination.total}


@http_service
def query_task_info(req):
    # 查询定时任务
    task = schedule_job_dao.select_by_no(req.jobNo)
    check_exists(task, error_msg='任务不存在')

    return {
        'jobNo': task.JOB_NO,
        'jobName': task.JOB_NAME,
        'jobDesc': task.JOB_DESC,
        'jobType': task.JOB_TYPE,
        'jobArgs': task.JOB_ARGS,
        'triggerType': task.TRIGGER_TYPE,
        'triggerArgs': task.TRIGGER_ARGS,
        'state': task.STATE
    }


@http_service
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
    check_not_exists(task, error_msg='相同内容的任务已存在')

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
        kwargs = {
            'start_date': req.triggerArgs.get('startDate', None) or None,
            'end_date': req.triggerArgs.get('endDate', None) or None,
            req.triggerArgs.type: int(req.triggerArgs.value)
        }
        apscheduler.add_job(
            id=job_no,
            name=req.jobName,
            func=TASK_FUNC.get(req.jobType),
            kwargs=req.jobArgs,
            trigger=req.triggerType.lower(),
            **kwargs
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

    # 新增历史记录
    TScheduleJobLog.insert(
        JOB_NO=job_no,
        LOG_NO=new_id(),
        OPERATION_TYPE=OperationType.ADD.value,
        OPERATION_BY=get_user_no(),
        OPERATION_TIME=datetime_now_by_utc8()
    )

    return {'jobNo': job_no}


@http_service
def modify_task(req):
    # 查询定时任务
    task = schedule_job_dao.select_by_no(req.jobNo)
    check_exists(task, error_msg='任务不存在')

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
    check_not_exists(existed_task, error_msg='相同内容的任务已存在')

    # 新增历史记录
    log_no = new_id()
    TScheduleJobLog.insert(
        JOB_NO=task.JOB_NO,
        LOG_NO=log_no,
        OPERATION_TYPE=OperationType.MODIFY.value,
        OPERATION_BY=get_user_no(),
        OPERATION_TIME=datetime_now_by_utc8()
    )
    # TODO: 记录任务修改详情

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
        kwargs = {
            'start_date': req.triggerArgs.get('startDate', None) or None,
            'end_date': req.triggerArgs.get('endDate', None) or None,
            req.triggerArgs.type: req.triggerArgs.value
        }
        apscheduler.modify_job(
            id=task.JOB_NO,
            name=req.jobName,
            kwargs=req.jobArgs,
            trigger=req.triggerType.lower(),
            **kwargs
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
def pause_task(req):
    # 查询定时任务
    task = schedule_job_dao.select_by_no(req.jobNo)
    check_exists(task, error_msg='任务不存在')

    # 校验空间权限
    check_workspace_permission(task.WORKSPACE_NO)

    # 暂停作业
    apscheduler.get_job(task.JOB_NO).pause()

    # 更新作业状态
    task.update(STATE=JobState.PAUSED.value)

    # 新增历史记录
    TScheduleJobLog.insert(
        JOB_NO=task.JOB_NO,
        LOG_NO=new_id(),
        OPERATION_TYPE=OperationType.PAUSE.value,
        OPERATION_BY=get_user_no(),
        OPERATION_TIME=datetime_now_by_utc8()
    )


@http_service
def resume_task(req):
    # 查询定时任务
    task = schedule_job_dao.select_by_no(req.jobNo)
    check_exists(task, error_msg='任务不存在')

    # 校验空间权限
    check_workspace_permission(task.WORKSPACE_NO)

    # 恢复作业
    apscheduler.get_job(task.JOB_NO).resume()

    # 更新作业状态
    task.update(STATE=JobState.NORMAL.value)

    # 新增历史记录
    TScheduleJobLog.insert(
        JOB_NO=task.JOB_NO,
        LOG_NO=new_id(),
        OPERATION_TYPE=OperationType.RESUME.value,
        OPERATION_BY=get_user_no(),
        OPERATION_TIME=datetime_now_by_utc8()
    )


@http_service
def remove_task(req):
    # 查询定时任务
    task = schedule_job_dao.select_by_no(req.jobNo)
    check_exists(task, error_msg='任务不存在')

    # 校验空间权限
    check_workspace_permission(task.WORKSPACE_NO)

    # 移除作业
    try:
        apscheduler.remove_job(task.JOB_NO)
    except JobLookupError:
        logger.info(f'jobNo:[{task.JOB_NO}] 作业不存在或已失效')

    # 更新作业状态
    task = schedule_job_dao.select_by_no(req.jobNo)
    if task and task.STATE != JobState.CLOSED.value:
        task.update(STATE=JobState.CLOSED.value)


@http_service
def query_task_history_list(req):
    # 查询条件
    conds = QueryCondition(TScheduleJobLog)
    conds.equal(TScheduleJobLog.JOB_NO, req.jobNo)
    conds.ge(TScheduleJobLog.CREATED_TIME, req.startTime)
    conds.le(TScheduleJobLog.CREATED_TIME, req.endTime)

    # 查询日志列表
    pagination = (
        dbquery(
            TScheduleJobLog.JOB_NO,
            TScheduleJobLog.OPERATION_TYPE,
            TScheduleJobLog.OPERATION_TIME,
            TScheduleJobLog.OPERATION_ARGS,
            TUser.USER_NAME
        )
        .outerjoin(TUser, TScheduleJobLog.OPERATION_BY == TUser.USER_NO)
        .filter(*conds)
        .order_by(TScheduleJobLog.CREATED_TIME.desc())
        .paginate(page=req.page, per_page=req.pageSize, error_out=False)
    )

    data = [
        {
            'jobNo': item.JOB_NO,
            'operationType': item.OPERATION_TYPE,
            'operationBy': item.USER_NAME,
            'operationTime': item.OPERATION_TIME,
            'operationContent': get_task_operation_content(item)
        }
        for item in pagination.items
    ]

    return {'data': data, 'total': pagination.total}


def get_task_operation_content(logrow):
    if logrow.OPERATION_TYPE == OperationType.EXECUTE.value:
        return to_json(logrow.OPERATION_ARGS)
    elif logrow.OPERATION_TYPE == OperationType.MODIFY.value:
        ...
    else:
        return
