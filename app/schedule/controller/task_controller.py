#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : task_controller.py
# @Time    : 2022/5/13 14:50
# @Author  : Kelvin.Ye
from app.common.decorators.require import require_login
from app.common.decorators.require import require_permission
from app.common.parser import Argument
from app.common.parser import JsonParser
from app.schedule.controller import blueprint
from app.schedule.enum import JobType
from app.schedule.enum import TriggerType
from app.schedule.service import task_service as service
from app.utils.log_util import get_logger


log = get_logger(__name__)


@blueprint.get('/task/list')
@require_login
@require_permission
def query_task_list():
    """分页查询定时任务列表"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('jobNo'),
        Argument('jobName'),
        Argument('jobDesc'),
        Argument('jobType'),
        Argument('triggerType'),
        Argument('state'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空'),
    ).parse()
    return service.query_task_list(req)


@blueprint.get('/task/info')
@require_login
@require_permission
def query_task_info():
    """查询定时任务信息"""
    req = JsonParser(
        Argument('jobNo', required=True, nullable=False, help='作业编号不能为空')
    ).parse()
    return service.query_task_info(req)


@blueprint.post('/task')
@require_login
@require_permission
def create_task():
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
    return service.create_task(req)


@blueprint.put('/task')
@require_login
@require_permission
def modify_task():
    """修改定时任务"""
    req = JsonParser(
        Argument('jobNo', required=True, nullable=False, help='作业编号不能为空'),
        Argument('jobName', required=True, nullable=False, help='作业名称不能为空'),
        Argument('jobDesc'),
        Argument('jobArgs', required=True, nullable=False, type=dict, help='作业参数不能为空'),
        Argument('triggerType', required=True, nullable=False, enum=TriggerType, help='触发器类型不能为空'),
        Argument('triggerArgs', required=True, nullable=False, type=dict, help='触发器参数不能为空')
    ).parse()
    return service.modify_task(req)


@blueprint.patch('/task/pause')
@require_login
@require_permission
def pause_task():
    """暂停定时任务"""
    req = JsonParser(
        Argument('jobNo', required=True, nullable=False, help='作业编号不能为空'),
    ).parse()
    return service.pause_task(req)


@blueprint.patch('/task/resume')
@require_login
@require_permission
def resume_task():
    """恢复定时任务"""
    req = JsonParser(
        Argument('jobNo', required=True, nullable=False, help='作业编号不能为空'),
    ).parse()
    return service.resume_task(req)


@blueprint.patch('/task/remove')
@require_login
@require_permission
def remove_task():
    """关闭定时任务"""
    req = JsonParser(
        Argument('jobNo', required=True, nullable=False, help='作业编号不能为空')
    ).parse()
    return service.remove_task(req)
