#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : tag_service.py
# @Time    : 2021-08-17 11:01:35
# @Author  : Kelvin.Ye
from app.public.dao import tag_dao as TagDao
from app.public.model import TTag
from app.tools.decorators.service import http_service
from app.tools.decorators.transaction import transactional
from app.tools.identity import new_id
from app.tools.logger import get_logger
from app.tools.validator import check_exists
from app.tools.validator import check_not_exists
from app.utils.sqlalchemy_util import QueryCondition


log = get_logger(__name__)


@http_service
def query_tag_list(req):
    # 查询条件
    conds = QueryCondition()
    conds.like(TTag.TAG_NO, req.tagNo)
    conds.like(TTag.TAG_NAME, req.tagName)
    conds.like(TTag.TAG_DESC, req.tagDesc)
    # 分页查询
    pagination = (
        TTag
        .filter(*conds)
        .order_by(TTag.CREATED_TIME.desc())
        .paginate(page=req.page, per_page=req.pageSize)
    )
    data = [
        {
            'tagNo': tag.WORKSPACE_NO,
            'tagName': tag.WORKSPACE_NAME,
            'tagDesc': tag.WORKSPACE_DESC
        }
        for tag in pagination.items
    ]
    return {'data': data, 'total': pagination.total}


@http_service
def query_tag_all():
    tags = TagDao.select_all()
    return [
        {
            'tagNo': tag.WORKSPACE_NO,
            'tagName': tag.WORKSPACE_NAME,
            'tagDesc': tag.WORKSPACE_DESC
        }
        for tag in tags
    ]


@http_service
@transactional
def create_tag(req):
    tag = TagDao.select_by_name(req.tagName)
    check_not_exists(tag, error_msg='标签已存在')

    TTag.insert(
        WORKSPACE_NO=new_id(),
        WORKSPACE_NAME=req.tagName,
        WORKSPACE_DESC=req.tagDesc
    )


@http_service
@transactional
def modify_tag(req):
    tag = TagDao.select_by_no(req.tagNo)
    check_exists(tag, error_msg='标签不存在')

    tag.update(
        WORKSPACE_NAME=req.tagName,
        WORKSPACE_DESC=req.tagDesc
    )


@http_service
@transactional
def remove_tag(req):
    tag = TagDao.select_by_no(req.tagNo)
    check_exists(tag, error_msg='标签不存在')

    tag.delete()
