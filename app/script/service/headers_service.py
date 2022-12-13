#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : headers_service.py
# @Time    : 2020/3/13 16:57
# @Author  : Kelvin.Ye
from app.database import dbquery
from app.public.enum import WorkspaceScope
from app.public.model import TWorkspace
from app.public.model import TWorkspaceUser
from app.script.dao import http_header_dao as HttpHeaderDao
from app.script.dao import http_header_template_dao as HttpheaderTemplateDao
from app.script.model import THttpHeader
from app.script.model import THttpHeaderTemplate
from app.tools import localvars
from app.tools.decorators.service import http_service
from app.tools.decorators.transaction import transactional
from app.tools.identity import new_id
from app.tools.logger import get_logger
from app.tools.validator import check_exists
from app.tools.validator import check_not_exists
from app.tools.validator import check_workspace_permission
from app.utils.sqlalchemy_util import QueryCondition


log = get_logger(__name__)


@http_service
def query_httpheader_template_list(req):
    # 查询条件
    conds = QueryCondition()
    conds.like(THttpHeaderTemplate.WORKSPACE_NO, req.workspaceNo)
    conds.like(THttpHeaderTemplate.TEMPLATE_NO, req.templateNo)
    conds.like(THttpHeaderTemplate.TEMPLATE_NAME, req.templateName)
    conds.like(THttpHeaderTemplate.TEMPLATE_DESC, req.templateDesc)

    # 分页查询
    pagination = (
        THttpHeaderTemplate
        .filter(*conds)
        .order_by(THttpHeaderTemplate.CREATED_TIME.desc())
        .paginate(page=req.page, per_page=req.pageSize)
    )

    data = [
        {
            'templateNo': item.TEMPLATE_NO,
            'templateName': item.TEMPLATE_NAME,
            'templateDesc': item.TEMPLATE_DESC
        }
        for item in pagination.items
    ]

    return {'data': data, 'total': pagination.total}


@http_service
def query_httpheader_template_all(req):
    conds = QueryCondition()
    conds.like(THttpHeaderTemplate.WORKSPACE_NO, req.workspaceNo)

    items = THttpHeaderTemplate.filter(*conds).order_by(THttpHeaderTemplate.CREATED_TIME.desc()).all()

    return [
        {
            'templateNo': item.TEMPLATE_NO,
            'templateName': item.TEMPLATE_NAME,
            'templateDesc': item.TEMPLATE_DESC
        }
        for item in items
    ]


@http_service
def query_httpheader_template_all_in_private():
    # 公共空间条件查询
    public_conds = QueryCondition(TWorkspace, THttpHeaderTemplate)
    public_conds.equal(TWorkspace.WORKSPACE_NO, THttpHeaderTemplate.WORKSPACE_NO)
    public_conds.equal(TWorkspace.WORKSPACE_SCOPE, WorkspaceScope.PUBLIC.value)
    public_filter = (
        dbquery(
            TWorkspace.WORKSPACE_NO,
            TWorkspace.WORKSPACE_NAME,
            TWorkspace.WORKSPACE_SCOPE,
            THttpHeaderTemplate.TEMPLATE_NO,
            THttpHeaderTemplate.TEMPLATE_NAME,
            THttpHeaderTemplate.TEMPLATE_DESC
        )
        .filter(*public_conds)
    )

    # 保护空间条件查询
    protected_conds = QueryCondition(TWorkspace, TWorkspaceUser, THttpHeaderTemplate)
    protected_conds.equal(TWorkspace.WORKSPACE_NO, TWorkspaceUser.WORKSPACE_NO)
    protected_conds.equal(TWorkspace.WORKSPACE_NO, THttpHeaderTemplate.WORKSPACE_NO)
    protected_conds.equal(TWorkspace.WORKSPACE_SCOPE, WorkspaceScope.PROTECTED.value)
    protected_conds.equal(TWorkspaceUser.USER_NO, localvars.get_user_no())
    protected_filter = (
        dbquery(
            TWorkspace.WORKSPACE_NO,
            TWorkspace.WORKSPACE_NAME,
            TWorkspace.WORKSPACE_SCOPE,
            THttpHeaderTemplate.TEMPLATE_NO,
            THttpHeaderTemplate.TEMPLATE_NAME,
            THttpHeaderTemplate.TEMPLATE_DESC
        )
        .filter(*protected_conds)
    )

    # 私人空间条件查询
    private_conds = QueryCondition(TWorkspace, TWorkspaceUser, THttpHeaderTemplate)
    private_conds.equal(TWorkspace.WORKSPACE_NO, TWorkspaceUser.WORKSPACE_NO)
    private_conds.equal(TWorkspace.WORKSPACE_NO, THttpHeaderTemplate.WORKSPACE_NO)
    private_conds.equal(TWorkspace.WORKSPACE_SCOPE, WorkspaceScope.PRIVATE.value)
    private_conds.equal(TWorkspaceUser.USER_NO, localvars.get_user_no())
    private_filter = (
        dbquery(
            TWorkspace.WORKSPACE_NO,
            TWorkspace.WORKSPACE_NAME,
            TWorkspace.WORKSPACE_SCOPE,
            THttpHeaderTemplate.TEMPLATE_NO,
            THttpHeaderTemplate.TEMPLATE_NAME,
            THttpHeaderTemplate.TEMPLATE_DESC
        )
        .filter(*private_conds)
    )

    items = (
        public_filter
        .union(protected_filter)
        .union(private_filter)
        .order_by(TWorkspace.WORKSPACE_SCOPE.desc())
        .all()
    )

    return [
        {
            'workspaceNo': item.WORKSPACE_NO,
            'workspaceName': item.WORKSPACE_NAME,
            'templateNo': item.TEMPLATE_NO,
            'templateName': item.TEMPLATE_NAME,
            'templateDesc': item.TEMPLATE_DESC
        }
        for item in items
    ]


@http_service
@transactional
def create_httpheader_template(req):
    # 校验空间权限
    check_workspace_permission(req.workspaceNo)

    # 查询模板
    template = HttpheaderTemplateDao.select_by_workspace_and_name(req.workspaceNo, req.templateName)
    check_not_exists(template, error_msg='模板已存在')

    # 新增模板
    template_no = new_id()
    THttpHeaderTemplate.insert(
        WORKSPACE_NO=req.workspaceNo,
        TEMPLATE_NO=template_no,
        TEMPLATE_NAME=req.templateName,
        TEMPLATE_DESC=req.templateDesc
    )

    return {'templateNo': template_no}


@http_service
@transactional
def modify_httpheader_template(req):
    # 查询模板
    template = HttpheaderTemplateDao.select_by_no(req.templateNo)
    check_exists(template, error_msg='模板不存在')

    # 校验空间权限
    check_workspace_permission(template.WORKSPACE_NO)

    # 更新模板
    template.update(
        TEMPLATE_NAME=req.templateName,
        TEMPLATE_DESC=req.templateDesc
    )


@http_service
@transactional
def remove_httpheader_template(req):
    # 查询模板
    template = HttpheaderTemplateDao.select_by_no(req.templateNo)
    check_exists(template, error_msg='模板不存在')
    # 校验空间权限
    check_workspace_permission(template.WORKSPACE_NO)
    # 删除模板下的所有请求头
    HttpHeaderDao.delete_all_by_template(req.templateNo)
    # 删除模板
    template.delete()


@http_service
@transactional
def create_http_header(req):
    # 查询请求头
    header = HttpHeaderDao.select_by_template_and_name(req.templateNo, req.headerName)
    check_not_exists(header, error_msg='请求头已存在')

    # 查询模板
    template = HttpheaderTemplateDao.select_by_no(req.templateNo)
    check_exists(template, error_msg='模板不存在')

    # 校验空间权限
    check_workspace_permission(template.WORKSPACE_NO)

    # 新增请求头
    header_no = new_id()
    THttpHeader.insert(
        TEMPLATE_NO=req.templateNo,
        HEADER_NO=header_no,
        HEADER_NAME=req.headerName.strip() if req.headerName else req.headerName,
        HEADER_VALUE=req.headerValue.strip() if req.headerValue else req.headerValue,
        HEADER_DESC=req.headerDesc,
        ENABLED=True
    )

    return header_no


@http_service
@transactional
def modify_http_header(req):
    # 查询请求头
    header = HttpHeaderDao.select_by_no(req.headerNo)
    check_exists(header, error_msg='请求头不存在')

    # 查询模板
    template = HttpheaderTemplateDao.select_by_no(header.TEMPLATE_NO)
    check_exists(template, error_msg='模板不存在')

    # 校验空间权限
    check_workspace_permission(template.WORKSPACE_NO)

    # 更新请求头
    header.update(
        HEADER_NAME=req.headerName.strip() if req.headerName else req.headerName,
        HEADER_VALUE=req.headerValue.strip() if req.headerValue else req.headerValue,
        HEADER_DESC=req.headerDesc
    )


@http_service
@transactional
def remove_http_header(req):
    # 查询请求头
    header = HttpHeaderDao.select_by_no(req.headerNo)
    check_exists(header, error_msg='请求头不存在')

    # 查询模板
    template = HttpheaderTemplateDao.select_by_no(header.TEMPLATE_NO)
    check_exists(template, error_msg='模板不存在')

    # 校验空间权限
    check_workspace_permission(template.WORKSPACE_NO)

    # 删除请求头
    header.delete()


@http_service
@transactional
def enable_http_header(req):
    # 查询请求头
    header = HttpHeaderDao.select_by_no(req.headerNo)
    check_exists(header, error_msg='请求头不存在')

    # 查询模板
    template = HttpheaderTemplateDao.select_by_no(header.TEMPLATE_NO)
    check_exists(template, error_msg='模板不存在')

    # 校验空间权限
    check_workspace_permission(template.WORKSPACE_NO)

    # 启用请求头
    header.update(
        ENABLED=True
    )


@http_service
@transactional
def disable_http_header(req):
    # 查询请求头
    header = HttpHeaderDao.select_by_no(req.headerNo)
    check_exists(header, error_msg='请求头不存在')

    # 查询模板
    template = HttpheaderTemplateDao.select_by_no(header.TEMPLATE_NO)
    check_exists(template, error_msg='模板不存在')

    # 校验空间权限
    check_workspace_permission(template.WORKSPACE_NO)

    # 禁用请求头
    header.update(
        ENABLED=False
    )


@http_service
@transactional
def query_http_headers_by_template(req):
    headers = HttpHeaderDao.select_all_by_template(req.templateNo)

    return [
        {
            'headerNo': header.HEADER_NO,
            'headerName': header.HEADER_NAME,
            'headerValue': header.HEADER_VALUE,
            'headerDesc': header.HEADER_DESC,
            'enabled': header.ENABLED
        }
        for header in headers
    ]


@http_service
def query_http_headers(req):
    result = []
    for template_no in req.list:
        # 查询模板
        template = HttpheaderTemplateDao.select_by_no(template_no)
        if not template:
            continue

        # 查询请求头列表
        headers = HttpHeaderDao.select_all_by_template(template_no)

        result.extend(
            {
                'headerNo': header.HEADER_NO,
                'headerName': header.HEADER_NAME,
                'headerValue': header.HEADER_VALUE,
                'headerDesc': header.HEADER_DESC,
                'enabled': header.ENABLED
            }
            for header in headers
        )

    return result


@http_service
@transactional
def create_http_headers(req):
    # 查询模板
    template = HttpheaderTemplateDao.select_by_no(req.templateNo)
    check_exists(template, error_msg='模板不存在')

    # 校验空间权限
    check_workspace_permission(template.WORKSPACE_NO)

    for header in req.headerList:
        # 跳过请求头为空的数据
        if not header.headerName:
            continue

        # 查询请求头
        entity = HttpHeaderDao.select_by_template_and_name(req.templateNo, header.headerName)
        check_not_exists(entity, error_msg='请求头已存在')

        # 新增请求头
        THttpHeader.insert(
            TEMPLATE_NO=req.templateNo,
            HEADER_NO=new_id(),
            HEADER_NAME=header.headerName.strip() if header.headerName else header.headerName,
            HEADER_VALUE=header.headerValue.strip() if header.headerValue else header.headerValue,
            HEADER_DESC=header.headerDesc,
            ENABLED=True
        )


@http_service
@transactional
def modify_http_headers(req):
    # 查询模板
    template = HttpheaderTemplateDao.select_by_no(req.templateNo)
    check_exists(template, error_msg='模板不存在')
    # 校验空间权限
    check_workspace_permission(template.WORKSPACE_NO)
    #  遍历更新请求头
    for header in req.headerList:
        # 跳过请求头为空的数据
        if not header.headerName:
            continue

        if 'headerNo' in header:
            # 查询请求头
            entity = HttpHeaderDao.select_by_no(header.headerNo)
            check_exists(entity, error_msg='请求头不存在')
            # 更新请求头
            entity.update(
                HEADER_NAME=header.headerName.strip() if header.headerName else header.headerName,
                HEADER_VALUE=header.headerValue.strip() if header.headerValue else header.headerValue,
                HEADER_DESC=header.headerDesc
            )
        else:
            # 查询请求头
            entity = HttpHeaderDao.select_by_template_and_name(req.templateNo, header.headerName)
            check_not_exists(entity, error_msg='请求头已存在')
            # 新增请求头
            THttpHeader.insert(
                TEMPLATE_NO=req.templateNo,
                HEADER_NO=new_id(),
                HEADER_NAME=header.headerName.strip() if header.headerName else header.headerName,
                HEADER_VALUE=header.headerValue.strip() if header.headerValue else header.headerValue,
                HEADER_DESC=header.headerDesc,
                ENABLED=True
            )


@http_service
@transactional
def remove_http_headers(req):
    # 查询模板
    template = HttpheaderTemplateDao.select_by_no(req.templateNo)
    check_exists(template, error_msg='模板不存在')
    # 校验空间权限
    check_workspace_permission(template.WORKSPACE_NO)
    # 批量删除请求头
    HttpHeaderDao.delete_in_no(req.headerNos)


@http_service
@transactional
def duplicate_httpheader_template(req):
    # 查询请求头模板
    template = HttpheaderTemplateDao.select_by_no(req.templateNo)
    check_exists(template, error_msg='请求头模板不存在')

    # 校验空间权限
    check_workspace_permission(template.WORKSPACE_NO)

    # 复制请求头模板
    new_template_no = new_id()
    THttpHeaderTemplate.insert(
        WORKSPACE_NO=template.WORKSPACE_NO,
        TEMPLATE_NO=new_template_no,
        TEMPLATE_NAME=f'{template.TEMPLATE_NAME} copy',
        TEMPLATE_DESC=template.TEMPLATE_DESC
    )

    # 复制请求头
    headers = HttpHeaderDao.select_all_by_template(req.templateNo)
    for header in headers:
        THttpHeader.insert(
            TEMPLATE_NO=new_template_no,
            HEADER_NO=new_id(),
            HEADER_NAME=header.HEADER_NAME,
            HEADER_VALUE=header.HEADER_VALUE,
            HEADER_DESC=header.HEADER_DESC,
            ENABLED=True
        )

    return {'templateNo': new_template_no}


@http_service
@transactional
def copy_httpheader_template_to_workspace(req):
    # 查询请求头模板
    template = HttpheaderTemplateDao.select_by_no(req.templateNo)
    check_exists(template, error_msg='请求头模板不存在')

    # 校验空间权限
    check_workspace_permission(template.WORKSPACE_NO)

    # 复制请求头模板
    new_template_no = new_id()
    THttpHeaderTemplate.insert(
        WORKSPACE_NO=req.workspaceNo,
        TEMPLATE_NO=new_template_no,
        TEMPLATE_NAME=f'{template.TEMPLATE_NAME} copy',
        TEMPLATE_DESC=template.TEMPLATE_DESC
    )

    # 复制请求头
    headers = HttpHeaderDao.select_all_by_template(req.templateNo)
    for header in headers:
        THttpHeader.insert(
            TEMPLATE_NO=new_template_no,
            HEADER_NO=new_id(),
            HEADER_NAME=header.HEADER_NAME,
            HEADER_VALUE=header.HEADER_VALUE,
            HEADER_DESC=header.HEADER_DESC,
            ENABLED=True
        )

    return {'templateNo': new_template_no}


@http_service
@transactional
def move_httpheader_template_to_workspace(req):
    # 校验空间权限
    check_workspace_permission(req.workspaceNo)
    # 查询请求头模板
    template = HttpheaderTemplateDao.select_by_no(req.templateNo)
    check_exists(template, error_msg='请求头模板不存在')
    # 移动请求头模板
    template.update(WORKSPACE_NO=req.workspaceNo)
