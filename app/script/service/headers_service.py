#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : headers_service.py
# @Time    : 2020/3/13 16:57
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.common.decorators.transaction import transactional
from app.common.id_generator import new_id
from app.common.validator import check_is_blank
from app.common.validator import check_is_not_blank
from app.script.dao import http_header_dao as HttpHeaderDao
from app.script.dao import http_header_template_dao as HttpHeaderTemplateDao
from app.script.model import THttpHeader
from app.script.model import THttpHeaderTemplate
from app.utils.log_util import get_logger


log = get_logger(__name__)


@http_service
def query_http_header_template_list(req):
    # 条件分页查询
    pagination = HttpHeaderTemplateDao.select_list(
        workspaceNo=req.workspaceNo,
        templateNo=req.templateNo,
        templateName=req.templateName,
        templateDesc=req.templateDesc,
        page=req.page,
        pageSize=req.pageSize
    )

    data = []
    for item in pagination.items:
        data.append({
            'templateNo': item.TEMPLATE_NO,
            'templateName': item.TEMPLATE_NAME,
            'templateDesc': item.TEMPLATE_DESC
        })
    return {'data': data, 'total': pagination.total}


@http_service
def query_http_header_template_all(req):
    # 条件查询
    items = HttpHeaderTemplateDao.select_all(
        workspaceNo=req.workspaceNo,
        templateNo=req.templateNo,
        templateName=req.templateName,
        templateDesc=req.templateDesc
    )

    result = []
    for item in items:
        result.append({
            'templateNo': item.TEMPLATE_NO,
            'templateName': item.TEMPLATE_NAME,
            'templateDesc': item.TEMPLATE_DESC
        })
    return result


@http_service
def create_http_header_template(req):
    # 查询模板
    template = HttpHeaderTemplateDao.select_by_workspace_and_name(req.workspaceNo, req.templateName)
    check_is_blank(template, '模板已存在')

    # 新增模板
    template_no = new_id()
    THttpHeaderTemplate.insert(
        WORKSPACE_NO=req.workspaceNo,
        TEMPLATE_NO=template_no,
        TEMPLATE_NAME=req.templateName,
        TEMPLATE_DESC=req.templateDesc
    )

    return template_no


@http_service
def modify_http_header_template(req):
    # 查询模板
    template = HttpHeaderTemplateDao.select_by_no(req.templateNo)
    check_is_not_blank(template, '模板不存在')

    # 更新模板
    template.update(
        TEMPLATE_NAME=req.templateName,
        TEMPLATE_DESC=req.templateDesc
    )


@http_service
def remove_http_header_template(req):
    # 查询模板
    template = HttpHeaderTemplateDao.select_by_no(req.templateNo)
    check_is_not_blank(template, '模板不存在')

    # 删除模板下的所有请求头
    HttpHeaderDao.delete_all_by_template(req.templateNo)
    # 删除模板
    template.delete()


@http_service
def create_http_header(req):
    # 查询请求头
    header = HttpHeaderDao.select_by_name(req.headerName)
    check_is_blank(header, '请求头已存在')

    # 查询模板
    template = HttpHeaderTemplateDao.select_by_no(req.templateNo)
    check_is_not_blank(template, '模板不存在')

    # 新增请求头
    header_no = new_id()
    THttpHeader.insert(
        TEMPLATE_NO=req.templateNo,
        HEADER_NO=header_no,
        HEADER_NAME=req.headerName,
        HEADER_VALUE=req.headerValue,
        HEADER_DESC=req.headerDesc,
        ENABLED=True
    )

    return header_no


@http_service
def modify_http_header(req):
    # 查询请求头
    header = HttpHeaderDao.select_by_no(req.headerNo)
    check_is_not_blank(header, '请求头不存在')

    # 更新请求头
    header.update(
        HEADER_NAME=req.headerName,
        HEADER_VALUE=req.headerValue,
        HEADER_DESC=req.headerDesc
    )


@http_service
def remove_http_header(req):
    # 查询请求头
    header = HttpHeaderDao.select_by_no(req.headerNo)
    check_is_not_blank(header, '请求头不存在')

    # 删除请求头
    header.delete()


@http_service
def enable_http_header(req):
    # 查询请求头
    header = HttpHeaderDao.select_by_no(req.headerNo)
    check_is_not_blank(header, '请求头不存在')

    # 启用请求头
    header.update(
        ENABLED=True
    )


@http_service
def disable_http_header(req):
    # 查询请求头
    header = HttpHeaderDao.select_by_no(req.headerNo)
    check_is_not_blank(header, '请求头不存在')

    # 禁用请求头
    header.update(
        ENABLED=False
    )


@http_service
def query_http_headers_by_template(req):
    headers = HttpHeaderDao.select_list_by_template(req.templateNo)

    result = []
    for header in headers:
        result.append({
            'headerNo': header.HEADER_NO,
            'headerName': header.HEADER_NAME,
            'headerValue': header.HEADER_VALUE,
            'headerDesc': header.HEADER_DESC,
            'enabled': header.ENABLED
        })
    return result


@http_service
def query_http_headers(req):
    result = []
    for template_no in req.list:
        # 查询模板
        template = HttpHeaderTemplateDao.select_by_no(template_no)
        if not template:
            continue

        # 查询请求头列表
        headers = HttpHeaderDao.select_list_by_template(template_no)

        for header in headers:
            result.append({
                'headerNo': header.HEADER_NO,
                'headerName': header.HEADER_NAME,
                'headerValue': header.HEADER_VALUE,
                'headerDesc': header.HEADER_DESC,
                'enabled': header.ENABLED
            })

    return result


@http_service
@transactional
def create_http_headers(req):
    # 查询模板
    template = HttpHeaderTemplateDao.select_by_no(req.templateNo)
    check_is_not_blank(template, '模板不存在')

    for header in req.headerList:
        # 跳过请求头为空的数据
        if not header.headerName:
            continue

        # 查询请求头
        entity = HttpHeaderDao.select_by_template_and_name(req.templateNo, header.headerName)
        check_is_blank(entity, '请求头已存在')

        # 新增请求头
        THttpHeader.insert(
            TEMPLATE_NO=req.templateNo,
            HEADER_NO=new_id(),
            HEADER_NAME=header.headerName,
            HEADER_VALUE=header.headerValue,
            HEADER_DESC=header.headerDesc,
            ENABLED=True
        )


@http_service
@transactional
def modify_http_headers(req):
    for header in req.headerList:
        # 跳过请求头为空的数据
        if not header.headerName:
            continue

        if 'headerNo' in header:
            # 查询请求头
            entity = HttpHeaderDao.select_by_no(header.headerNo)
            check_is_not_blank(entity, '请求头不存在')
            # 更新请求头
            entity.update(
                HEADER_NAME=header.headerName,
                HEADER_VALUE=header.headerValue,
                HEADER_DESC=header.headerDesc
            )
        else:
            # 查询请求头
            entity = HttpHeaderDao.select_by_template_and_name(req.templateNo, header.headerName)
            check_is_blank(entity, '请求头已存在')
            # 新增请求头
            THttpHeader.insert(
                TEMPLATE_NO=req.templateNo,
                HEADER_NO=new_id(),
                HEADER_NAME=header.headerName,
                HEADER_VALUE=header.headerValue,
                HEADER_DESC=header.headerDesc,
                ENABLED=True
            )


@http_service
def remove_http_headers(req):
    # 批量删除请求头
    HttpHeaderDao.delete_in_no(req.list)


@http_service
@transactional
def duplicate_http_header_template(req):
    # 查询请求头模板
    template = HttpHeaderTemplateDao.select_by_no(req.templateNo)
    check_is_not_blank(template, '请求头模板不存在')

    # 复制请求头模板
    template_no = new_id()
    THttpHeaderTemplate.insert(
        WORKSPACE_NO=template.WORKSPACE_NO,
        TEMPLATE_NO=template_no,
        TEMPLATE_NAME=template.TEMPLATE_NAME + ' copy',
        TEMPLATE_DESC=template.TEMPLATE_DESC
    )

    # 复制请求头
    headers = HttpHeaderDao.select_list_by_template(req.templateNo)
    for header in headers:
        THttpHeader.insert(
            TEMPLATE_NO=req.templateNo,
            HEADER_NO=new_id(),
            HEADER_NAME=header.HEADER_NAME,
            HEADER_VALUE=header.HEADER_VALUE,
            HEADER_DESC=header.HEADER_DESC,
            ENABLED=True
        )

    return {'templateNo': template_no}


@http_service
@transactional
def copy_http_header_template_to_workspace(req):
    # 查询请求头模板
    template = HttpHeaderTemplateDao.select_by_no(req.templateNo)
    check_is_not_blank(template, '请求头模板不存在')

    # 复制请求头模板
    template_no = new_id()
    THttpHeaderTemplate.insert(
        WORKSPACE_NO=req.workspaceNo,
        TEMPLATE_NO=template_no,
        TEMPLATE_NAME=template.TEMPLATE_NAME + ' copy',
        TEMPLATE_DESC=template.TEMPLATE_DESC
    )

    # 复制请求头
    headers = HttpHeaderDao.select_list_by_template(req.templateNo)
    for header in headers:
        THttpHeader.insert(
            TEMPLATE_NO=req.templateNo,
            HEADER_NO=new_id(),
            HEADER_NAME=header.HEADER_NAME,
            HEADER_VALUE=header.HEADER_VALUE,
            HEADER_DESC=header.HEADER_DESC,
            ENABLED=True
        )

    return {'templateNo': template_no}


@http_service
def move_http_header_template_to_workspace(req):
    # 查询请求头模板
    template = HttpHeaderTemplateDao.select_by_no(req.templateNo)
    check_is_not_blank(template, '请求头模板不存在')

    template.update(WORKSPACE_NO=req.workspaceNo)
