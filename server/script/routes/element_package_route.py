#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : element_package
# @Time    : 2020/3/17 14:31
# @Author  : Kelvin.Ye
from server.librarys.decorators.require import require_login, require_permission
from server.librarys.parser import JsonParser, Argument
from server.script.routes import blueprint
from server.script.services import element_package_service as service
from server.utils.log_util import get_logger

log = get_logger(__name__)


@blueprint.route('/element/package/list', methods=['GET'])
@require_login
@require_permission
def element_package_list():
    """分页查询元素封装列表
    """
    req = JsonParser(
        Argument('No', required=True, nullable=False, help=''),
    ).parse()
    return service.element_package_list(req)


@blueprint.route('/element/package/all', methods=['GET'])
@require_login
@require_permission
def element_package_all():
    """查询所有元素封装
    """
    req = JsonParser(
        Argument('No', required=True, nullable=False, help=''),
    ).parse()
    return service.element_package_all(req)
