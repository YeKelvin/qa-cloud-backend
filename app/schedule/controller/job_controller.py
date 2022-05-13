#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : job_controller.py
# @Time    : 2022/5/13 14:50
# @Author  : Kelvin.Ye
from app.common.decorators.require import require_login
from app.common.decorators.require import require_permission
from app.common.parser import Argument
from app.common.parser import JsonParser
from app.schedule.controller import blueprint
from app.schedule.enum import JobType
from app.schedule.enum import TriggerType
from app.schedule.service import job_service as service
from app.utils.log_util import get_logger


log = get_logger(__name__)


@blueprint.get('/job/list')
@require_login
@require_permission
def query_schedule_job_list():
    """分页查询定时任务列表"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('jobNo'),
        Argument('jobName'),
        Argument('jobDesc'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空'),
    ).parse()
    return service.query_schedule_job_list(req)


@blueprint.get('/job/all')
@require_login
@require_permission
def query_schedule_job_all():
    """查询所有定时任务"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='工作空间编号不能为空')
    ).parse()
    return service.query_schedule_job_all(req)


@blueprint.get('/job/info')
@require_login
@require_permission
def query_schedule_job_info():
    """查询定时任务信息"""
    req = JsonParser(
        Argument('jobNo', required=True, nullable=False, help='作业编号不能为空')
    ).parse()
    return service.query_schedule_job_info(req)


@blueprint.post('/job')
@require_login
@require_permission
def create_schedule_job():
    """新增定时任务"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='空间编号不能为空'),
        Argument('jobName', required=True, nullable=False, help='作业名称不能为空'),
        Argument('jobDesc'),
        Argument('jobType', required=True, nullable=False, enum=JobType, help='作业类型不能为空'),
        Argument('jobArgs', required=True, nullable=False, type=dict, help='作业参数不能为空'),
        Argument('triggerType', required=True, nullable=False, enum=TriggerType, help='触发器类型不能为空'),
        Argument('triggerArgs', required=True, nullable=False, type=dict, help='触发器参数不能为空')
    ).parse()
    return service.create_schedule_job(req)


@blueprint.put('/job')
@require_login
@require_permission
def modify_schedule_job():
    """修改定时任务"""
    req = JsonParser(
        Argument('jobNo', required=True, nullable=False, help='作业编号不能为空'),
        Argument('jobName', required=True, nullable=False, help='作业名称不能为空'),
        Argument('jobDesc'),
        Argument('jobType', required=True, nullable=False, enum=JobType, help='作业类型不能为空'),
        Argument('jobArgs', required=True, nullable=False, type=dict, help='作业参数不能为空'),
        Argument('triggerType', required=True, nullable=False, enum=TriggerType, help='触发器类型不能为空'),
        Argument('triggerArgs', required=True, nullable=False, type=dict, help='触发器参数不能为空')
    ).parse()
    return service.modify_schedule_job(req)


@blueprint.patch('/job/pause')
@require_login
@require_permission
def pause_schedule_job():
    """暂停定时任务"""
    req = JsonParser(
        Argument('jobNo', required=True, nullable=False, help='作业编号不能为空'),
    ).parse()
    return service.pause_schedule_job(req)


@blueprint.patch('/job/resume')
@require_login
@require_permission
def resume_schedule_job():
    """恢复定时任务"""
    req = JsonParser(
        Argument('jobNo', required=True, nullable=False, help='作业编号不能为空'),
    ).parse()
    return service.resume_schedule_job(req)


@blueprint.delete('/job/shutdown')
@require_login
@require_permission
def shutdown_schedule_job():
    """关闭定时任务"""
    req = JsonParser(
        Argument('jobNo', required=True, nullable=False, help='作业编号不能为空'),
        Argument('wait', default=True),
    ).parse()
    return service.shutdown_schedule_job(req)
