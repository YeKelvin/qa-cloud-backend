#!/usr/bin python3
# @File    : history_controller.py
# @Time    : 2023-10-08 15:50:19
# @Author  : Kelvin.Ye
from app.modules.script.controller import blueprint
from app.modules.script.service import history_service as service
from app.tools.parser import Argument
from app.tools.parser import JsonParser
from app.tools.require import require_login
from app.tools.require import require_permission


@blueprint.get('/element/changelog/list')
@require_login
@require_permission('QUERY_ELEMENT')
def query_element_changelog_list():
    """分页查询操作日志列表"""
    req = JsonParser(
        Argument('elementNo'),
        Argument('order', default='desc'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空')
    ).parse()
    return service.query_element_changelog_list(req)
