#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : route.py
# @Time    : 2019/11/14 9:50
# @Author  : Kelvin.Ye
from flask import Blueprint

from server.librarys.decorators.require import require_login, require_permission
from server.librarys.parser import JsonParser, Argument
from server.user import service
from server.utils.log_util import get_logger

log = get_logger(__name__)

blueprint = Blueprint('script', __name__, url_prefix='/script')


@blueprint.route('/item', methods=['POST'])
def item_list():
    """分页查询测试项目列表
    """
    pass


@blueprint.route('/item', methods=['POST'])
def item_all():
    """查询所有测试项目
    """
    pass


@blueprint.route('/item', methods=['POST'])
def create_item():
    """新增测试项目
    """
    pass


@blueprint.route('/item', methods=['POST'])
def modify_item():
    """修改测试项目
    """
    pass


@blueprint.route('/item', methods=['POST'])
def delete_item():
    """删除测试项目
    """
    pass
