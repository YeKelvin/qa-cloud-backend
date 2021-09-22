#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : report_controller.py
# @Time    : 2021/9/22 14:20
# @Author  : Kelvin.Ye
from app.common.decorators.require import require_login
from app.common.decorators.require import require_permission
from app.common.parser import Argument
from app.common.parser import JsonParser
from app.script.controller import blueprint
from app.script.service import report_service as service
from app.utils.log_util import get_logger


log = get_logger(__name__)


@blueprint.get('/report/collection/result')
@require_login
@require_permission
def query_collection_result():
    """根据 collectionId 查询 Collection 结果和 Group 结果列表"""
    req = JsonParser(Argument('collectionId', required=True, nullable=False, help='collectionId不能为空')).parse()
    return service.query_collection_result(req)


@blueprint.get('/report/group/result')
@require_login
@require_permission
def query_group_result():
    """根据 groupId 查询 Group 结果"""
    req = JsonParser(Argument('groupId', required=True, nullable=False, help='groupId不能为空')).parse()
    return service.query_group_result(req)


@blueprint.get('/report/sampler/result')
@require_login
@require_permission
def query_sampler_result():
    """根据 samplerId 查询 Sampler 结果"""
    req = JsonParser(Argument('samplerId', required=True, nullable=False, help='samplerId不能为空')).parse()
    return service.query_sampler_result(req)
