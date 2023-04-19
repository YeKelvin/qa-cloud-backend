#!/usr/bin/ python3
# @File    : job_controller.py
# @Time    : 2022/5/20 11:15
# @Author  : Kelvin.Ye
from app.schedule.controller import blueprint
from app.schedule.service import job_service as service
from app.tools.decorators.require import require_login
from app.tools.decorators.require import require_permission
from app.tools.parser import Argument
from app.tools.parser import JsonParser


@blueprint.get('/job/info')
@require_login
@require_permission('QUERY_JOB')
def query_job_info():
    """查询作业信息"""
    req = JsonParser(
        Argument('jobNo', required=True, nullable=False, help='作业编号不能为空')
    ).parse()
    return service.query_job_info(req)


@blueprint.post('/job/run')
@require_login
@require_permission('RUN_JOB')
def run_job():
    """立即运行作业"""
    req = JsonParser(
        Argument('jobNo', required=True, nullable=False, help='作业编号不能为空')
    ).parse()
    return service.run_job(req)
