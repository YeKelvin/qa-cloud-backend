#!/usr/bin/ python3
# @File    : httpheader_service.py
# @Time    : 2020/3/13 16:57
# @Author  : Kelvin.Ye
from app.modules.script.dao import http_header_dao
from app.modules.script.dao import httpheader_template_dao
from app.modules.script.model import THttpHeader
from app.modules.script.model import THttpHeaderTemplate
from app.tools.identity import new_id
from app.tools.service import http_service
from app.tools.validator import check_exists
from app.tools.validator import check_not_exists
from app.tools.validator import check_workspace_permission
from app.utils.sqlalchemy_util import QueryCondition


@http_service
def query_template_list(req):
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
        .paginate(page=req.page, per_page=req.pageSize, error_out=False)
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
def query_template_all(req):
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
def create_template(req):
    # 校验空间权限
    check_workspace_permission(req.workspaceNo)

    # 查询模板
    template = httpheader_template_dao.select_by_workspace_and_name(req.workspaceNo, req.templateName)
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
def modify_template(req):
    # 查询模板
    template = httpheader_template_dao.select_by_no(req.templateNo)
    check_exists(template, error_msg='模板不存在')

    # 校验空间权限
    check_workspace_permission(template.WORKSPACE_NO)

    # 更新模板
    template.update(
        TEMPLATE_NAME=req.templateName,
        TEMPLATE_DESC=req.templateDesc
    )


@http_service
def remove_template(req):
    # 查询模板
    template = httpheader_template_dao.select_by_no(req.templateNo)
    check_exists(template, error_msg='模板不存在')
    # 校验空间权限
    check_workspace_permission(template.WORKSPACE_NO)
    # 删除模板下的所有请求头
    http_header_dao.delete_all_by_template(req.templateNo)
    # 删除模板
    template.delete()


@http_service
def create_http_header(req):
    # 查询请求头
    header = http_header_dao.select_by_template_and_name(req.templateNo, req.headerName)
    check_not_exists(header, error_msg='请求头已存在')

    # 查询模板
    template = httpheader_template_dao.select_by_no(req.templateNo)
    check_exists(template, error_msg='模板不存在')

    # 校验空间权限
    check_workspace_permission(template.WORKSPACE_NO)

    # 新增请求头
    header_no = new_id()
    THttpHeader.insert(
        TEMPLATE_NO=req.templateNo,
        HEADER_NO=header_no,
        HEADER_NAME=req.headerName.strip() if req.headerName else req.headerName,
        HEADER_DESC=req.headerDesc,
        HEADER_VALUE=req.headerValue.strip() if req.headerValue else req.headerValue,
        ENABLED=True
    )

    return header_no


@http_service
def modify_http_header(req):
    # 查询请求头
    header = http_header_dao.select_by_no(req.headerNo)
    check_exists(header, error_msg='请求头不存在')

    # 查询模板
    template = httpheader_template_dao.select_by_no(header.TEMPLATE_NO)
    check_exists(template, error_msg='模板不存在')

    # 校验空间权限
    check_workspace_permission(template.WORKSPACE_NO)

    # 更新请求头
    header.update(
        HEADER_NAME=req.headerName.strip() if req.headerName else req.headerName,
        HEADER_DESC=req.headerDesc,
        HEADER_VALUE=req.headerValue.strip() if req.headerValue else req.headerValue
    )


@http_service
def remove_http_header(req):
    # 查询请求头
    header = http_header_dao.select_by_no(req.headerNo)
    check_exists(header, error_msg='请求头不存在')

    # 查询模板
    template = httpheader_template_dao.select_by_no(header.TEMPLATE_NO)
    check_exists(template, error_msg='模板不存在')

    # 校验空间权限
    check_workspace_permission(template.WORKSPACE_NO)

    # 删除请求头
    header.delete()


@http_service
def enable_http_header(req):
    # 查询请求头
    header = http_header_dao.select_by_no(req.headerNo)
    check_exists(header, error_msg='请求头不存在')

    # 查询模板
    template = httpheader_template_dao.select_by_no(header.TEMPLATE_NO)
    check_exists(template, error_msg='模板不存在')

    # 校验空间权限
    check_workspace_permission(template.WORKSPACE_NO)

    # 启用请求头
    header.update(
        ENABLED=True
    )


@http_service
def disable_http_header(req):
    # 查询请求头
    header = http_header_dao.select_by_no(req.headerNo)
    check_exists(header, error_msg='请求头不存在')

    # 查询模板
    template = httpheader_template_dao.select_by_no(header.TEMPLATE_NO)
    check_exists(template, error_msg='模板不存在')

    # 校验空间权限
    check_workspace_permission(template.WORKSPACE_NO)

    # 禁用请求头
    header.update(
        ENABLED=False
    )


@http_service
def query_httpheaders_by_template(req):
    headers = http_header_dao.select_all_by_template(req.templateNo)

    return [
        {
            'headerNo': header.HEADER_NO,
            'headerName': header.HEADER_NAME,
            'headerDesc': header.HEADER_DESC,
            'headerValue': header.HEADER_VALUE,
            'enabled': header.ENABLED
        }
        for header in headers
    ]


@http_service
def query_httpheaders(req):
    result = []
    for template_no in req.templates:
        # 查询模板
        template = httpheader_template_dao.select_by_no(template_no)
        if not template:
            continue

        # 查询请求头列表
        headers = http_header_dao.select_all_by_template(template_no)

        result.extend(
            {
                'headerNo': header.HEADER_NO,
                'headerName': header.HEADER_NAME,
                'headerDesc': header.HEADER_DESC,
                'headerValue': header.HEADER_VALUE,
                'enabled': header.ENABLED
            }
            for header in headers
        )

    return result


@http_service
def create_httpheaders(req):
    # 查询模板
    template = httpheader_template_dao.select_by_no(req.templateNo)
    check_exists(template, error_msg='模板不存在')

    # 校验空间权限
    check_workspace_permission(template.WORKSPACE_NO)

    for header in req.headerList:
        # 跳过请求头为空的数据
        if not header.headerName:
            continue

        # 查询请求头
        entity = http_header_dao.select_by_template_and_name(req.templateNo, header.headerName)
        check_not_exists(entity, error_msg=f'请求头:[ {header.headerName} ] 请求头已存在')

        # 新增请求头
        THttpHeader.insert(
            TEMPLATE_NO=req.templateNo,
            HEADER_NO=new_id(),
            HEADER_NAME=header.headerName.strip() if header.headerName else header.headerName,
            HEADER_DESC=header.headerDesc,
            HEADER_VALUE=header.headerValue.strip() if header.headerValue else header.headerValue,
            ENABLED=True
        )


@http_service
def modify_httpheaders(req):
    # 查询模板
    template = httpheader_template_dao.select_by_no(req.templateNo)
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
            entity = http_header_dao.select_by_no(header.headerNo)
            check_exists(entity, error_msg='请求头不存在')
            # 更新请求头
            entity.update(
                HEADER_NAME=header.headerName.strip() if header.headerName else header.headerName,
                HEADER_DESC=header.headerDesc,
                HEADER_VALUE=header.headerValue.strip() if header.headerValue else header.headerValue,
                ENABLED=header.enabled
            )
        else:
            # 查询请求头
            entity = http_header_dao.select_by_template_and_name(req.templateNo, header.headerName)
            check_not_exists(entity, error_msg=f'请求头:[ {header.headerName} ] 请求头已存在')
            # 新增请求头
            THttpHeader.insert(
                TEMPLATE_NO=req.templateNo,
                HEADER_NO=new_id(),
                HEADER_NAME=header.headerName.strip() if header.headerName else header.headerName,
                HEADER_DESC=header.headerDesc,
                HEADER_VALUE=header.headerValue.strip() if header.headerValue else header.headerValue,
                ENABLED=header.enabled
            )


@http_service
def remove_httpheaders(req):
    # 查询模板
    template = httpheader_template_dao.select_by_no(req.templateNo)
    check_exists(template, error_msg='模板不存在')
    # 校验空间权限
    check_workspace_permission(template.WORKSPACE_NO)
    # 批量删除请求头
    http_header_dao.delete_in_no(req.headers)


@http_service
def duplicate_template(req):
    # 查询请求头模板
    template = httpheader_template_dao.select_by_no(req.templateNo)
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
    headers = http_header_dao.select_all_by_template(req.templateNo)
    for header in headers:
        THttpHeader.insert(
            TEMPLATE_NO=new_template_no,
            HEADER_NO=new_id(),
            HEADER_NAME=header.HEADER_NAME,
            HEADER_DESC=header.HEADER_DESC,
            HEADER_VALUE=header.HEADER_VALUE,
            ENABLED=True
        )

    return {'templateNo': new_template_no}


@http_service
def copy_template_to_workspace(req):
    # 查询请求头模板
    template = httpheader_template_dao.select_by_no(req.templateNo)
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
    headers = http_header_dao.select_all_by_template(req.templateNo)
    for header in headers:
        THttpHeader.insert(
            TEMPLATE_NO=new_template_no,
            HEADER_NO=new_id(),
            HEADER_NAME=header.HEADER_NAME,
            HEADER_DESC=header.HEADER_DESC,
            HEADER_VALUE=header.HEADER_VALUE,
            ENABLED=True
        )

    return {'templateNo': new_template_no}


@http_service
def move_template_to_workspace(req):
    # 校验空间权限
    check_workspace_permission(req.workspaceNo)
    # 查询请求头模板
    template = httpheader_template_dao.select_by_no(req.templateNo)
    check_exists(template, error_msg='请求头模板不存在')
    # 移动请求头模板
    template.update(WORKSPACE_NO=req.workspaceNo)
