#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : execution_helper.py
# @Time    : 2021/1/22 23:41
# @Author  : Kelvin.Ye
from app.common.validator import assert_not_blank
from app.script.model import TElementChildRel
from app.script.model import TElementProperty
from app.script.model import TTestElement
from app.utils.log_util import get_logger


log = get_logger(__name__)


def element_to_dict(element_no):
    # 查询元素
    element = TTestElement.query_by(ELEMENT_NO=element_no).first()
    assert_not_blank(element, '测试元素不存在')

    # 递归查询元素子代
    # 查询时根据order asc排序
    element_child_rels = TElementChildRel.query_by(PARENT_NO=element_no).order_by(TElementChildRel.CHILD_ORDER).all()
    children = []
    if element_child_rels:
        for element_child_rel in element_child_rels:
            children.append(element_to_dict(element_child_rel.CHILD_NO))

    # 组装dict返回
    el_dict = {
        'name': element.ELEMENT_NAME,
        'comments': element.ELEMENT_REMARK,
        'class': element.ELEMENT_CLASS,
        'enabled': element.ENABLED,
        'property': property_to_dict(element_no),
        'child': children
    }
    return el_dict


def property_to_dict(element_no):
    # 查询元素属性，只查询enabled的属性
    props = TElementProperty.query_by(ELEMENT_NO=element_no, ENABLED=True).all()

    # 组装dict返回
    prop_dict = {}
    for prop in props:
        prop_dict[prop.PROPERTY_NAME] = prop.PROPERTY_VALUE

    return prop_dict
