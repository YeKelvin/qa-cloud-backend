#!/usr/bin python3
# @File    : running_service.py
# @Time    : 2023-04-20 14:34:59
# @Author  : Kelvin.Ye
from app.modules.script.service.execution_service import run_testplan
from app.tools.service import open_service


@open_service
def execute_testplan(req):
    return run_testplan(req.planNo, req.datasets, req.useCurrentValue)
