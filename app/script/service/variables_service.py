#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : variables_service.py
# @Time    : 2020/3/13 16:59
# @Author  : Kelvin.Ye
from sqlalchemy import and_

from app.common import globals
from app.common.decorators.service import http_service
from app.common.decorators.transaction import transactional
from app.common.identity import new_id
from app.common.logger import get_logger
from app.common.validator import check_exists
from app.common.validator import check_not_exists
from app.common.validator import check_workspace_permission
from app.database import dbquery
from app.public.enum import WorkspaceScope
from app.public.model import TWorkspace
from app.public.model import TWorkspaceUser
from app.script.dao import variable_dao as VariableDao
from app.script.dao import variable_dataset_dao as VariableDatasetDao
from app.script.enum import VariableDatasetType
from app.script.enum import VariableDatasetWeight
from app.script.model import TVariable
from app.script.model import TVariableDataset
from app.utils.sqlalchemy_util import QueryCondition


log = get_logger(__name__)


@http_service
def query_variables_dataset_list(req):
    # 条件查询
    conds = QueryCondition()
    conds.like(TVariableDataset.WORKSPACE_NO, req.workspaceNo)
    conds.like(TVariableDataset.DATASET_NO, req.datasetNo)
    conds.like(TVariableDataset.DATASET_NAME, req.datasetName)
    conds.like(TVariableDataset.DATASET_TYPE, req.datasetType)
    conds.like(TVariableDataset.DATASET_DESC, req.datasetDesc)

    # 条件分页查询
    pagination = (
        TVariableDataset
        .filter(*conds)
        .order_by(TVariableDataset.CREATED_TIME.desc())
        .paginate(req.page, req.pageSize)
    )

    data = [
        {
            'datasetNo': item.DATASET_NO,
            'datasetName': item.DATASET_NAME,
            'datasetType': item.DATASET_TYPE,
            'datasetDesc': item.DATASET_DESC
        }
        for item in pagination.items
    ]

    return {'data': data, 'total': pagination.total}


@http_service
def query_variable_dataset_all(req):
    # 条件查询
    conds = QueryCondition()
    conds.equal(TVariableDataset.WORKSPACE_NO, req.workspaceNo)
    conds.equal(TVariableDataset.DATASET_TYPE, req.datasetType)

    results = (
        TVariableDataset
        .filter(and_(*conds) | (TVariableDataset.DATASET_TYPE == VariableDatasetType.GLOBAL.value))
        .order_by(TVariableDataset.CREATED_TIME.desc())
        .all()
    )

    return [
        {
            'datasetNo': item.DATASET_NO,
            'datasetName': item.DATASET_NAME,
            'datasetType': item.DATASET_TYPE,
            'datasetDesc': item.DATASET_DESC
        }
        for item in results
    ]


@http_service
def query_variable_dataset_all_in_private(req):
    # 公共空间条件查询
    public_conds = QueryCondition(TWorkspace, TVariableDataset)
    public_conds.equal(TWorkspace.WORKSPACE_NO, TVariableDataset.WORKSPACE_NO)
    public_conds.equal(TWorkspace.WORKSPACE_SCOPE, WorkspaceScope.PUBLIC.value)
    public_conds.equal(TVariableDataset.DATASET_TYPE, req.datasetType)
    public_filter = (
        dbquery(
            TWorkspace.WORKSPACE_NO,
            TWorkspace.WORKSPACE_NAME,
            TWorkspace.WORKSPACE_SCOPE,
            TVariableDataset.DATASET_NO,
            TVariableDataset.DATASET_NAME,
            TVariableDataset.DATASET_TYPE,
            TVariableDataset.DATASET_DESC
        )
        .filter(and_(*public_conds) | (TVariableDataset.DATASET_TYPE == VariableDatasetType.GLOBAL.value))
    )

    # 保护空间条件查询
    protected_conds = QueryCondition(TWorkspace, TWorkspaceUser, TVariableDataset)
    protected_conds.equal(TWorkspace.WORKSPACE_NO, TWorkspaceUser.WORKSPACE_NO)
    protected_conds.equal(TWorkspace.WORKSPACE_NO, TVariableDataset.WORKSPACE_NO)
    protected_conds.equal(TWorkspace.WORKSPACE_SCOPE, WorkspaceScope.PROTECTED.value)
    protected_conds.equal(TWorkspaceUser.USER_NO, globals.get_userno())
    protected_conds.equal(TVariableDataset.DATASET_TYPE, req.datasetType)
    protected_filter = (
        dbquery(
            TWorkspace.WORKSPACE_NO,
            TWorkspace.WORKSPACE_NAME,
            TWorkspace.WORKSPACE_SCOPE,
            TVariableDataset.DATASET_NO,
            TVariableDataset.DATASET_NAME,
            TVariableDataset.DATASET_TYPE,
            TVariableDataset.DATASET_DESC
        )
        .filter(and_(*protected_conds) | (TVariableDataset.DATASET_TYPE == VariableDatasetType.GLOBAL.value))
    )

    # 私人空间条件查询
    private_conds = QueryCondition(TWorkspace, TWorkspaceUser, TVariableDataset)
    private_conds.equal(TWorkspace.WORKSPACE_NO, TWorkspaceUser.WORKSPACE_NO)
    private_conds.equal(TWorkspace.WORKSPACE_NO, TVariableDataset.WORKSPACE_NO)
    private_conds.equal(TWorkspace.WORKSPACE_SCOPE, WorkspaceScope.PRIVATE.value)
    private_conds.equal(TWorkspaceUser.USER_NO, globals.get_userno())
    private_conds.equal(TVariableDataset.DATASET_TYPE, req.datasetType)
    private_filter = (
        dbquery(
            TWorkspace.WORKSPACE_NO,
            TWorkspace.WORKSPACE_NAME,
            TWorkspace.WORKSPACE_SCOPE,
            TVariableDataset.DATASET_NO,
            TVariableDataset.DATASET_NAME,
            TVariableDataset.DATASET_TYPE,
            TVariableDataset.DATASET_DESC
        )
        .filter(and_(*private_conds) | (TVariableDataset.DATASET_TYPE == VariableDatasetType.GLOBAL.value))
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
def create_variable_dataset(req):
    # 校验空间权限
    check_workspace_permission(req.workspaceNo)

    # 查询变量集信息
    dataset = VariableDatasetDao.select_first(
        WORKSPACE_NO=req.workspaceNo,
        DATASET_NAME=req.datasetName,
        DATASET_TYPE=req.datasetType
    )
    check_not_exists(dataset, '变量集已存在')

    # 变量集为ENVIRONMENT或CUSTOM时，工作空间编号不能为空
    if req.datasetType != VariableDatasetType.GLOBAL.value:
        check_exists(req.workspaceNo, '工作空间编号不能为空')

    # 新增变量集
    dataset_no = new_id()
    TVariableDataset.insert(
        WORKSPACE_NO=req.workspaceNo,
        DATASET_NO=dataset_no,
        DATASET_NAME=req.datasetName,
        DATASET_TYPE=req.datasetType,
        DATASET_DESC=req.datasetDesc,
        WEIGHT=VariableDatasetWeight[req.datasetType].value
    )

    return {'datasetNo': dataset_no}


@http_service
@transactional
def modify_variable_dataset(req):
    # 查询变量集信息
    dataset = VariableDatasetDao.select_by_no(req.datasetNo)
    check_exists(dataset, '变量集不存在')

    # 校验空间权限
    check_workspace_permission(dataset.WORKSPACE_NO)

    # 更新变量集信息
    dataset.update(
        DATASET_NAME=req.datasetName,
        DATASET_DESC=req.datasetDesc
    )


@http_service
@transactional
def remove_variable_dataset(req):
    # 查询变量集信息
    dataset = VariableDatasetDao.select_by_no(req.datasetNo)
    check_exists(dataset, '变量集不存在')
    # 校验空间权限
    check_workspace_permission(dataset.WORKSPACE_NO)
    # 删除变量集下的所有变量
    VariableDao.delete_all_by_dataset(req.datasetNo)
    # 删除变量集
    dataset.delete()


@http_service
@transactional
def create_variable(req):
    # 查询变量信息
    variable = VariableDao.select_by_dataset_and_name(req.datasetNo, req.varName)
    check_not_exists(variable, '变量集已存在')

    # 查询变量集信息
    dataset = VariableDatasetDao.select_by_no(req.datasetNo)
    check_exists(dataset, '变量集不存在')

    # 校验空间权限
    check_workspace_permission(dataset.WORKSPACE_NO)

    # 新增变量
    var_no = new_id()
    TVariable.insert(
        DATASET_NO=req.datasetNo,
        VAR_NO=var_no,
        VAR_NAME=req.varName,
        VAR_DESC=req.varDesc,
        INITIAL_VALUE=req.initialValue,
        CURRENT_VALUE=req.currentValue,
        ENABLED=True
    )

    return var_no


@http_service
@transactional
def modify_variable(req):
    # 查询变量信息
    variable = VariableDao.select_by_no(req.varNo)
    check_exists(variable, '变量不存在')

    # 查询变量集信息
    dataset = VariableDatasetDao.select_by_no(variable.DATASET_NO)
    check_exists(dataset, '变量集不存在')

    # 校验空间权限
    check_workspace_permission(dataset.WORKSPACE_NO)

    # 更新变量信息
    variable.update(
        VAR_NAME=req.varName,
        VAR_DESC=req.varDesc,
        INITIAL_VALUE=req.initialValue,
        CURRENT_VALUE=req.currentValue
    )


@http_service
@transactional
def remove_variable(req):
    # 查询变量信息
    variable = VariableDao.select_by_no(req.varNo)
    check_exists(variable, '变量不存在')

    # 查询变量集信息
    dataset = VariableDatasetDao.select_by_no(variable.DATASET_NO)
    check_exists(dataset, '变量集不存在')

    # 校验空间权限
    check_workspace_permission(dataset.WORKSPACE_NO)

    # 删除变量
    variable.delete()


@http_service
@transactional
def enable_variable(req):
    # 查询变量信息
    variable = VariableDao.select_by_no(req.varNo)
    check_exists(variable, '变量不存在')

    # 查询变量集信息
    dataset = VariableDatasetDao.select_by_no(variable.DATASET_NO)
    check_exists(dataset, '变量集不存在')

    # 校验空间权限
    check_workspace_permission(dataset.WORKSPACE_NO)

    # 启用变量
    variable.update(
        ENABLED=True
    )


@http_service
@transactional
def disable_variable(req):
    # 查询变量信息
    variable = VariableDao.select_by_no(req.varNo)
    check_exists(variable, '变量不存在')

    # 查询变量集信息
    dataset = VariableDatasetDao.select_by_no(variable.DATASET_NO)
    check_exists(dataset, '变量集不存在')

    # 校验空间权限
    check_workspace_permission(dataset.WORKSPACE_NO)

    # 禁用变量
    variable.update(
        ENABLED=False
    )


@http_service
@transactional
def update_current_value(req):
    # 查询变量信息
    variable = VariableDao.select_by_no(req.varNo)
    check_exists(variable, '变量不存在')

    # 查询变量集信息
    dataset = VariableDatasetDao.select_by_no(variable.DATASET_NO)
    check_exists(dataset, '变量集不存在')

    # 校验空间权限
    check_workspace_permission(dataset.WORKSPACE_NO)

    # 更新当前值
    variable.update(
        CURRENT_VALUE=req.value
    )


@http_service
def query_variable_by_dataset(req):
    variables = VariableDao.select_all_by_dataset(req.datasetNo)

    return [
        {
            'varNo': variable.VAR_NO,
            'varName': variable.VAR_NAME,
            'varDesc': variable.VAR_DESC,
            'initialValue': variable.INITIAL_VALUE,
            'currentValue': variable.CURRENT_VALUE,
            'enabled': variable.ENABLED
        }
        for variable in variables
    ]


@http_service
def query_variables(req):
    result = []
    for dataset_no in req.list:
        # 查询变量集信息
        dataset = VariableDatasetDao.select_by_no(dataset_no)
        if not dataset:
            continue

        # 查询变量列表
        variables = VariableDao.select_all_by_dataset(dataset_no)

        result.extend(
            {
                'datasetNo': dataset.DATASET_NO,
                'datasetName': dataset.DATASET_NAME,
                'varNo': variable.VAR_NO,
                'varName': variable.VAR_NAME,
                'varDesc': variable.VAR_DESC,
                'initialValue': variable.INITIAL_VALUE,
                'currentValue': variable.CURRENT_VALUE,
                'enabled': variable.ENABLED
            }
            for variable in variables
        )

    return result


@http_service
@transactional
def create_variables(req):
    # 查询变量集信息
    dataset = VariableDatasetDao.select_by_no(req.datasetNo)
    check_exists(dataset, '变量集不存在')

    # 校验空间权限
    check_workspace_permission(dataset.WORKSPACE_NO)

    for vari in req.variableList:
        # 跳过变量名为空的数据
        if not vari.varName:
            continue

        # 查询变量信息
        variable = VariableDao.select_by_dataset_and_name(req.datasetNo, vari.varName)
        check_not_exists(variable, '变量已存在')

        # 新增变量
        TVariable.insert(
            DATASET_NO=req.datasetNo,
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
    # 查询变量集信息
    dataset = VariableDatasetDao.select_by_no(req.datasetNo)
    check_exists(dataset, '变量集不存在')
    # 校验空间权限
    check_workspace_permission(dataset.WORKSPACE_NO)
    # 遍历更新变量
    for vari in req.variableList:
        # 跳过变量名为空的数据
        if not vari.varName:
            continue

        if 'varNo' in vari:
            # 查询变量信息
            variable = VariableDao.select_by_no(vari.varNo)
            check_exists(variable, '变量不存在')
            # 更新变量信息
            variable.update(
                VAR_NAME=vari.varName,
                VAR_DESC=vari.varDesc,
                INITIAL_VALUE=vari.initialValue,
                CURRENT_VALUE=vari.currentValue
            )
        else:
            # 查询变量信息
            variable = VariableDao.select_by_dataset_and_name(req.datasetNo, vari.varName)
            check_not_exists(variable, '变量已存在')
            # 新增变量
            TVariable.insert(
                DATASET_NO=req.datasetNo,
                VAR_NO=new_id(),
                VAR_NAME=vari.varName,
                VAR_DESC=vari.varDesc,
                INITIAL_VALUE=vari.initialValue,
                CURRENT_VALUE=vari.currentValue,
                ENABLED=True
            )


@http_service
@transactional
def remove_variables(req):
    # 查询变量集信息
    dataset = VariableDatasetDao.select_by_no(req.datasetNo)
    check_exists(dataset, '变量集不存在')
    # 校验空间权限
    check_workspace_permission(dataset.WORKSPACE_NO)
    # 批量删除变量
    VariableDao.delete_in_no(req.variableNumberedList)


@http_service
@transactional
def duplicate_variable_dataset(req):
    # 查询变量集
    dataset = VariableDatasetDao.select_by_no(req.datasetNo)
    check_exists(dataset, '变量集不存在')

    # 校验空间权限
    check_workspace_permission(dataset.WORKSPACE_NO)

    # 复制变量集
    new_dataset_no = new_id()
    TVariableDataset.insert(
        WORKSPACE_NO=dataset.WORKSPACE_NO,
        DATASET_NO=new_dataset_no,
        DATASET_NAME=f'{dataset.DATASET_NAME} copy',
        DATASET_TYPE=dataset.DATASET_TYPE,
        DATASET_DESC=dataset.DATASET_DESC,
        WEIGHT=dataset.WEIGHT
    )

    # 复制变量
    variables = VariableDao.select_all_by_dataset(req.datasetNo)
    for variable in variables:
        TVariable.insert(
            DATASET_NO=new_dataset_no,
            VAR_NO=new_id(),
            VAR_NAME=variable.VAR_NAME,
            VAR_DESC=variable.VAR_DESC,
            INITIAL_VALUE=variable.INITIAL_VALUE,
            CURRENT_VALUE=variable.CURRENT_VALUE,
            ENABLED=True
        )

    return {'datasetNo': new_dataset_no}


@http_service
@transactional
def copy_variable_dataset_to_workspace(req):
    # 查询变量集
    dataset = VariableDatasetDao.select_by_no(req.datasetNo)
    check_exists(dataset, '变量集不存在')

    # 校验空间权限
    check_workspace_permission(dataset.WORKSPACE_NO)

    # 复制变量集
    new_dataset_no = new_id()
    TVariableDataset.insert(
        WORKSPACE_NO=req.workspaceNo,
        DATASET_NO=new_dataset_no,
        DATASET_NAME=f'{dataset.DATASET_NAME} copy',
        DATASET_TYPE=dataset.DATASET_TYPE,
        DATASET_DESC=dataset.DATASET_DESC,
        WEIGHT=dataset.WEIGHT
    )

    # 复制变量
    variables = VariableDao.select_all_by_dataset(req.datasetNo)
    for variable in variables:
        TVariable.insert(
            DATASET_NO=new_dataset_no,
            VAR_NO=new_id(),
            VAR_NAME=variable.VAR_NAME,
            VAR_DESC=variable.VAR_DESC,
            INITIAL_VALUE=variable.INITIAL_VALUE,
            CURRENT_VALUE=variable.CURRENT_VALUE,
            ENABLED=True
        )

    return {'datasetNo': new_dataset_no}


@http_service
@transactional
def move_variable_dataset_to_workspace(req):
    # 校验空间权限
    check_workspace_permission(req.workspaceNo)
    # 查询变量集
    dataset = VariableDatasetDao.select_by_no(req.datasetNo)
    check_exists(dataset, '变量集不存在')
    # 移动变量集
    dataset.update(WORKSPACE_NO=req.workspaceNo)
