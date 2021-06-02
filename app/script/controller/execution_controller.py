#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : execution_controller.py
# @Time    : 2020/3/20 15:00
# @Author  : Kelvin.Ye
from app.common.decorators.require import require_login
from app.common.decorators.require import require_permission
from app.common.parser import Argument
from app.common.parser import JsonParser
from app.script.controller import blueprint
from app.script.service import execution_service as service
from app.utils.log_util import get_logger


log = get_logger(__name__)


@blueprint.post('/execute')
@require_login
@require_permission
def execute_script():
    """运行脚本
    """
    req = JsonParser(
        Argument('collectionNo', required=True, nullable=False, help='集合编号不能为空'),
        Argument('sid')
    ).parse()
    return service.execute_script(req)
