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


log = get_logger(__name__)


@http_service
def query_tag_list(req):
    tags = TagDao.select_list(
        tagNo=req.tagNo,
        tagName=req.tagName,
        tagDesc=req.tagDesc,
        page=req.page,
        pageSize=req.pageSize
    )

    data = []
    for tag in tags.items:
        data.append({
            'tagNo': tag.WORKSPACE_NO,
            'tagName': tag.WORKSPACE_NAME,
            'tagDesc': tag.WORKSPACE_DESC
        })
    return {'data': data, 'total': tags.total}


@http_service
def query_tag_all():
    tags = TagDao.select_all()
    result = []
    for tag in tags:
        result.append({
            'tagNo': tag.WORKSPACE_NO,
            'tagName': tag.WORKSPACE_NAME,
            'tagDesc': tag.WORKSPACE_DESC
        })
    return result


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
