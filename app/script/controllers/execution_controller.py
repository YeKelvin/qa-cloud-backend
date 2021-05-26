#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : execution_route
# @Time    : 2020/3/20 15:00
# @Author  : Kelvin.Ye
from app.common.decorators.require import require_login, require_permission
from app.common.parser import JsonParser, Argument
from app.script.controllers import blueprint
from app.script.services import execution_service as service
from app.utils.log_util import get_logger

log = get_logger(__name__)


@blueprint.route('/execute', methods=['POST'])
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
