#!/usr/bin/ python3
# @File    : tpa_service.py
# @Time    : 2023-04-17 17:15:40
# @Author  : Kelvin.Ye
from app.modules.opencenter.dao import third_party_application_dao
from app.modules.opencenter.enum import APPState
from app.modules.opencenter.model import TThirdPartyApplication
from app.tools.exceptions import ServiceError
from app.tools.identity import new_id
from app.tools.identity import new_ulid
from app.tools.service import http_service
from app.tools.validator import check_exists
from app.utils.sqlalchemy_util import QueryCondition


@http_service
def query_application_list(req):
    # 查询应用列表
    conds = QueryCondition()
    conds.like(TThirdPartyApplication.APP_NO, req.appNo)
    conds.like(TThirdPartyApplication.APP_NAME, req.appName)
    conds.like(TThirdPartyApplication.APP_CODE, req.appCode)
    conds.like(TThirdPartyApplication.APP_DESC, req.appDesc)
    conds.like(TThirdPartyApplication.STATE, req.state)

    pagination = (
        TThirdPartyApplication
        .filter(*conds)
        .order_by(TThirdPartyApplication.CREATED_TIME.desc())
        .paginate(page=req.page, per_page=req.pageSize)
    )

    data = [
        {
            'appNo': tpa.APP_NO,
            'appName': tpa.APP_NAME,
            'appCode': tpa.APP_CODE,
            'appDesc': tpa.APP_DESC,
            'appSecret': tpa.APP_SECRET,
            'state': tpa.STATE
        }
        for tpa in pagination.items
    ]

    return {'data': data, 'total': pagination.total}


@http_service
def query_application_info(req):
    # 查询应用
    tpa = third_party_application_dao.select_by_no(req.appNo)
    check_exists(tpa, error_msg='应用不存在')

    return {
        'appNo': tpa.APP_NO,
        'appName': tpa.APP_NAME,
        'appCode': tpa.APP_CODE,
        'appDesc': tpa.APP_DESC,
        'state': tpa.STATE
    }


@http_service
def create_application(req):
    # 唯一性校验
    if third_party_application_dao.select_by_name(req.appName):
        raise ServiceError('应用名称已存在')
    if third_party_application_dao.select_by_code(req.appCode):
        raise ServiceError('应用代码已存在')

    # 创建应用
    app_no = new_id()
    TThirdPartyApplication.insert(
        APP_NO=app_no,
        APP_NAME=req.appName,
        APP_CODE=req.appCode,
        APP_DESC=req.appDesc,
        APP_SECRET=new_ulid(),
        STATE=APPState.ENABLE.value
    )

    return {'appNo': app_no}


@http_service
def modify_application(req):
    # 查询应用
    tpa = third_party_application_dao.select_by_no(req.appNo)
    check_exists(tpa, error_msg='应用不存在')

    # 唯一性校验
    if tpa.APP_NAME != req.appName and third_party_application_dao.select_by_name(req.appName):
        raise ServiceError('应用名称已存在')
    if tpa.APP_CODE != req.appCode and third_party_application_dao.select_by_code(req.appCode):
        raise ServiceError('应用代码已存在')

    # 更新应用信息
    tpa.update(
        APP_NAME=req.appName,
        APP_CODE=req.appCode,
        APP_DESC=req.appDesc
    )


@http_service
def modify_application_state(req):
    # 查询应用
    tpa = third_party_application_dao.select_by_no(req.appNo)
    check_exists(tpa, error_msg='应用不存在')

    # 更新应用状态
    tpa.update(STATE=req.state)


@http_service
def reset_application_secret(req):
    # 查询应用
    tpa = third_party_application_dao.select_by_no(req.appNo)
    check_exists(tpa, error_msg='应用不存在')

    # 重置应用密钥
    tpa.update(
        APP_SECRET=new_ulid()
    )


@http_service
def remove_application(req):
    # 查询应用
    tpa = third_party_application_dao.select_by_no(req.appNo)
    check_exists(tpa, error_msg='应用不存在')

    # 删除应用
    tpa.delete()
