#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : variables_service.py
# @Time    : 2020/3/13 16:59
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.common.decorators.transaction import transactional
from app.common.id_generator import new_id
from app.common.validator import check_is_blank
from app.common.validator import check_is_not_blank
from app.script.dao import variable_dao as VariableDao
from app.script.dao import variable_set_dao as VariableSetDao
from app.script.enum import VariableSetType
from app.script.enum import VariableSetWeight
from app.script.model import TVariable
from app.script.model import TVariableSet
from app.utils.log_util import get_logger


log = get_logger(__name__)


@http_service
def query_variables_set_list(req):
    # 条件分页查询
    pagination = VariableSetDao.select_list(
        workspaceNo=req.workspaceNo,
        setNo=req.setNo,
        setName=req.setName,
        setType=req.setType,
        setDesc=req.setDesc,
        page=req.page,
        pageSize=req.pageSize
    )

    data = []
    for item in pagination.items:
        data.append({
            'setNo': item.SET_NO,
            'setName': item.SET_NAME,
            'setType': item.SET_TYPE,
            'setDesc': item.SET_DESC
        })
    return {'data': data, 'total': pagination.total}


@http_service
def query_variable_set_all(req):
    # 条件查询
    items = VariableSetDao.select_all(
        workspaceNo=req.workspaceNo,
        setNo=req.setNo,
        setName=req.setName,
        setType=req.setType,
        setDesc=req.setDesc
    )

    result = []
    for item in items:
        result.append({
            'setNo': item.SET_NO,
            'setName': item.SET_NAME,
            'setType': item.SET_TYPE,
            'setDesc': item.SET_DESC
        })
    return result


@http_service
def query_variable_set(req):
    variables = VariableDao.select_list_by_set(req.setNo)

    result = []
    for variable in variables:
        result.append({
            'varNo': variable.VAR_NO,
            'varName': variable.VAR_NAME,
            'varDesc': variable.VAR_DESC,
            'initialValue': variable.INITIAL_VALUE,
            'currentValue': variable.CURRENT_VALUE,
            'enabled': variable.ENABLED
        })
    return result


@http_service
def create_variable_set(req):
    # 查询变量集信息
    varset = VariableSetDao.select_first(WORKSPACE_NO=req.workspaceNo, SET_NAME=req.setName, SET_TYPE=req.setType)
    check_is_blank(varset, '变量集已存在')

    # 变量集为ENVIRONMENT或CUSTOM时，工作空间编号不能为空
    if req.setType != VariableSetType.GLOBAL.value:
        check_is_not_blank(req.workspaceNo, '工作空间编号不能为空')

    # 新增变量集
    set_no = new_id()
    TVariableSet.insert(
        WORKSPACE_NO=req.workspaceNo,
        SET_NO=set_no,
        SET_NAME=req.setName,
        SET_TYPE=req.setType,
        SET_DESC=req.setDesc,
        WEIGHT=VariableSetWeight[req.setType].value
    )

    return set_no


@http_service
def modify_variable_set(req):
    # 查询变量集信息
    varset = VariableSetDao.select_by_no(req.setNo)
    check_is_not_blank(varset, '变量集不存在')

    # 更新变量集信息
    varset.update(
        SET_NAME=req.setName,
        SET_DESC=req.setDesc
    )


@http_service
def delete_variable_set(req):
    # 查询变量集信息
    varset = VariableSetDao.select_by_no(req.setNo)
    check_is_not_blank(varset, '变量集不存在')

    # 删除变量集，TODO: 还要删除变量集下的变量
    varset.delete()


@http_service
def create_variable(req):
    # 查询变量信息
    variable = VariableDao.select_by_name(req.varName)
    check_is_blank(variable, '变量集已存在')

    # 查询变量集信息
    varset = VariableSetDao.select_by_no(req.setNo)
    check_is_not_blank(varset, '变量集不存在')

    # 新增变量
    var_no = new_id()
    TVariable.insert(
        SET_NO=req.setNo,
        VAR_NO=var_no,
        VAR_NAME=req.varName,
        VAR_DESC=req.varDesc,
        INITIAL_VALUE=req.initialValue,
        CURRENT_VALUE=req.currentValue,
        ENABLED=True
    )

    return var_no


@http_service
def modify_variable(req):
    # 查询变量信息
    variable = VariableDao.select_by_no(req.varNo)
    check_is_not_blank(variable, '变量不存在')

    # 更新变量信息
    variable.update(
        VAR_NAME=req.varName,
        VAR_DESC=req.varDesc,
        INITIAL_VALUE=req.initialValue,
        CURRENT_VALUE=req.currentValue
    )


@http_service
def delete_variable(req):
    # 查询变量信息
    variable = VariableDao.select_by_no(req.varNo)
    check_is_not_blank(variable, '变量不存在')

    # 删除变量
    variable.delete()


@http_service
def enable_variable(req):
    # 查询变量信息
    variable = VariableDao.select_by_no(req.varNo)
    check_is_not_blank(variable, '变量不存在')

    # 启用变量
    variable.update(
        ENABLED=True
    )


@http_service
def disable_variable(req):
    # 查询变量信息
    variable = VariableDao.select_by_no(req.varNo)
    check_is_not_blank(variable, '变量不存在')

    # 禁用变量
    variable.update(
        ENABLED=False
    )


@http_service
def update_current_value(req):
    # 查询变量信息
    variable = VariableDao.select_by_no(req.varNo)
    check_is_not_blank(variable, '变量不存在')

    # 更新当前值
    variable.update(
        CURRENT_VALUE=req.value
    )


@http_service
def query_variables(req):
    result = []
    for set_no in req.list:
        # 查询变量集信息
        set = VariableSetDao.select_by_no(set_no)
        if not set:
            continue

        # 查询变量列表
        variables = VariableDao.select_list_by_set(set_no)

        for variable in variables:
            result.append({
                'setNo': set.SET_NO,
                'setName': set.SET_NAME,
                'varNo': variable.VAR_NO,
                'varName': variable.VAR_NAME,
                'varDesc': variable.VAR_DESC,
                'initialValue': variable.INITIAL_VALUE,
                'currentValue': variable.CURRENT_VALUE,
                'enabled': variable.ENABLED
            })
    return result


@http_service
@transactional
def create_variables(req):
    # 查询变量集信息
    varset = VariableSetDao.select_by_no(req.setNo)
    check_is_not_blank(varset, '变量集不存在')

    for vari in req.varList:
        # 跳过变量名为空的数据
        if not vari.varName:
            continue

        # 查询变量信息
        variable = VariableDao.select_by_set_and_name(req.setNo, vari.varName)
        check_is_blank(variable, '变量已存在')

        # 新增变量
        TVariable.insert(
            SET_NO=req.setNo,
            VAR_NO=new_id(),
            VAR_NAME=vari.varName,
            VAR_DESC=vari.varDesc,
            INITIAL_VALUE=vari.initialValue,
            CURRENT_VALUE=vari.currentValue,
            ENABLED=True
        )


@http_service
@transactional
def modify_variables(req):
    for vari in req.varList:
        # 跳过变量名为空的数据
        if not vari.varName:
            continue

        if 'varNo' in vari:
            # 查询变量信息
            variable = VariableDao.select_by_no(vari.varNo)
            check_is_not_blank(variable, '变量不存在')
            # 更新变量信息
            variable.update(
                VAR_NAME=vari.varName,
                VAR_DESC=vari.varDesc,
                INITIAL_VALUE=vari.initialValue,
                CURRENT_VALUE=vari.currentValue
            )
        else:
            # 查询变量信息
            variable = VariableDao.select_by_set_and_name(req.setNo, vari.varName)
            check_is_blank(variable, '变量已存在')
            # 新增变量
            TVariable.insert(
                SET_NO=req.setNo,
                VAR_NO=new_id(),
                VAR_NAME=vari.varName,
                VAR_DESC=vari.varDesc,
                INITIAL_VALUE=vari.initialValue,
                CURRENT_VALUE=vari.currentValue,
                ENABLED=True
            )


@http_service
def delete_variables(req):
    # 批量删除变量
    VariableDao.delete_in_no(req.list)
