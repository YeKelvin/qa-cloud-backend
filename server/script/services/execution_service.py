#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : execution_service
# @Time    : 2020/3/20 15:00
# @Author  : Kelvin.Ye
from server.common.decorators.service import http_service
from server.common.request import RequestDTO
from server.common.utils.log_util import get_logger
from server.common.validator import assert_not_blank
from server.script.models import TElementChildRel, TTestElement

log = get_logger(__name__)


@http_service
def execute_script(req: RequestDTO):
    # 查询测试集合
    collection = TTestElement.query_by(ELEMENT_NO=req.attr.collectionNo).first()
    assert_not_blank(collection, '测试元素不存在')

    # 遍历查询测试组
    collection_children = TElementChildRel.query_by(ELEMENT_NO=req.attr.collectionNo).all()
    groups = []
    for child in collection_children:
        group = TTestElement.query_by(ELEMENT_NO=child.ELEMENT_NO).first()
        assert_not_blank(group, '测试元素不存在')
        groups.append(group)

    pass
