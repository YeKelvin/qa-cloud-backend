#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : tag_service.py
# @Time    : 2021-08-17 11:01:35
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.common.id_generator import new_id
from app.common.validator import check_is_blank
from app.common.validator import check_is_not_blank
from app.public.dao import tag_dao as TagDao
from app.public.model import TTag
from app.utils.log_util import get_logger


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
def create_tag(req):
    tag = TagDao.select_by_tagname(req.tagName)
    check_is_blank(tag, '标签已存在')

    TTag.insert(
        WORKSPACE_NO=new_id(),
        WORKSPACE_NAME=req.tagName,
        WORKSPACE_DESC=req.tagDesc
    )


@http_service
def modify_tag(req):
    tag = TagDao.select_by_tagno(req.tagNo)
    check_is_not_blank(tag, '标签不存在')

    tag.update(
        WORKSPACE_NAME=req.tagName,
        WORKSPACE_DESC=req.tagDesc
    )


@http_service
def delete_tag(req):
    tag = TagDao.select_by_tagno(req.tagNo)
    check_is_not_blank(tag, '标签不存在')

    tag.delete()
