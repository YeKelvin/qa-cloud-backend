#!/usr/bin/ python3
# @File    : job_controller.py
# @Time    : 2022/5/13 14:50
# @Author  : Kelvin.Ye
from app.modules.schedule.controller import blueprint
from app.modules.schedule.enum import JobType
from app.modules.schedule.enum import TriggerType
from app.modules.schedule.service import job_service as service
from app.tools.parser import Argument
from app.tools.parser import JsonParser
from app.tools.require import require_login
from app.tools.require import require_permission


@blueprint.get('/job/list')
@require_login
@require_permission('QUERY_JOB')
def query_job_list():
    """分页查询定时任务列表"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('jobNo'),
        Argument('jobName'),
        Argument('jobDesc'),
        Argument('jobType'),
        Argument('jobState'),
        Argument('triggerType'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空')
    ).parse()
    return service.query_job_list(req)


@blueprint.get('/job/info')
@require_login
@require_permission('QUERY_JOB')
def query_job_info():
    """查询任务信息"""
    req = JsonParser(
        Argument('jobNo', required=True, nullable=False, help='作业编号不能为空')
    ).parse()
    return service.query_job_info(req)


@blueprint.post('/job')
@require_login
@require_permission('CREATE_JOB')
def create_job():
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
    return service.create_job(req)


@blueprint.put('/job')
@require_login
@require_permission('MODIFY_JOB')
def modify_job():
    """修改定时任务"""
    req = JsonParser(
        Argument('jobNo', required=True, nullable=False, help='作业编号不能为空'),
        Argument('jobName', required=True, nullable=False, help='作业名称不能为空'),
        Argument('jobDesc'),
        Argument('jobArgs', required=True, nullable=False, type=dict, help='作业参数不能为空'),
        Argument('triggerType', required=True, nullable=False, enum=TriggerType, help='触发器类型不能为空'),
        Argument('triggerArgs', required=True, nullable=False, type=dict, help='触发器参数不能为空')
    ).parse()
    return service.modify_job(req)


@blueprint.put('/job/pause')
@require_login
@require_permission('PAUSE_JOB')
def pause_job():
    """暂停定时任务"""
    req = JsonParser(
        Argument('jobNo', required=True, nullable=False, help='作业编号不能为空'),
    ).parse()
    return service.pause_job(req)


@blueprint.put('/job/resume')
@require_login
@require_permission('RESUME_JOB')
def resume_job():
    """恢复定时任务"""
    req = JsonParser(
        Argument('jobNo', required=True, nullable=False, help='作业编号不能为空'),
    ).parse()
    return service.resume_job(req)


@blueprint.put('/job/remove')
@require_login
@require_permission('REMOVE_JOB')
def remove_job():
    """关闭定时任务"""
    req = JsonParser(
        Argument('jobNo', required=True, nullable=False, help='作业编号不能为空')
    ).parse()
    return service.remove_job(req)


@blueprint.get('/job/log/list')
@require_login
@require_permission('QUERY_JOB')
def query_job_log_list():
    """分业查询任务历史列表"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='空间编号不能为空'),
        Argument('logNo'),
        Argument('jobNo'),
        Argument('jobName'),
        Argument('jobEvent'),
        Argument('startTime'),
        Argument('endTime'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空')
    ).parse()
    return service.query_job_log_list(req)
