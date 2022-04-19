#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : variables_service.py
# @Time    : 2020/3/13 16:59
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.common.decorators.transaction import transactional
from app.common.id_generator import new_id
from app.common.validator import check_not_exists
from app.common.validator import check_exists
from app.script.dao import variable_dao as VariableDao
from app.script.dao import variable_dataset_dao as VariableDatasetDao
from app.script.enum import VariableDatasetType
from app.script.enum import VariableDatasetWeight
from app.script.model import TVariable
from app.script.model import TVariableDataset
from app.utils.log_util import get_logger


log = get_logger(__name__)


@http_service
def query_variables_dataset_list(req):
    # 条件分页查询
    pagination = VariableDatasetDao.select_list(
        workspaceNo=req.workspaceNo,
        datasetNo=req.datasetNo,
        datasetName=req.datasetName,
        datasetType=req.datasetType,
        datasetDesc=req.datasetDesc,
        page=req.page,
        pageSize=req.pageSize
    )

    data = []
    for item in pagination.items:
        data.append({
            'datasetNo': item.DATASET_NO,
            'datasetName': item.DATASET_NAME,
            'datasetType': item.DATASET_TYPE,
            'datasetDesc': item.DATASET_DESC
        })
    return {'data': data, 'total': pagination.total}


@http_service
def query_variable_dataset_all(req):
    # 条件查询
    items = VariableDatasetDao.select_all(
        workspaceNo=req.workspaceNo,
        datasetNo=req.datasetNo,
        datasetName=req.datasetName,
        datasetType=req.datasetType,
        datasetDesc=req.datasetDesc
    )

    result = []
    for item in items:
        result.append({
            'datasetNo': item.DATASET_NO,
            'datasetName': item.DATASET_NAME,
            'datasetType': item.DATASET_TYPE,
            'datasetDesc': item.DATASET_DESC
        })
    return result


@http_service
@transactional
def create_variable_dataset(req):
    # 查询变量集信息
    varset = VariableDatasetDao.select_first(
        WORKSPACE_NO=req.workspaceNo,
        DATASET_NAME=req.datasetName,
        DATASET_TYPE=req.datasetType
    )
    check_not_exists(varset, '变量集已存在')

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
    varset = VariableDatasetDao.select_by_no(req.datasetNo)
    check_exists(varset, '变量集不存在')

    # 更新变量集信息
    varset.update(
        DATASET_NAME=req.datasetName,
        DATASET_DESC=req.datasetDesc
    )


@http_service
@transactional
def remove_variable_dataset(req):
    # 查询变量集信息
    dataset = VariableDatasetDao.select_by_no(req.datasetNo)
    check_exists(dataset, '变量集不存在')

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

    # 删除变量
    variable.delete()


@http_service
@transactional
def enable_variable(req):
    # 查询变量信息
    variable = VariableDao.select_by_no(req.varNo)
    check_exists(variable, '变量不存在')

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

    # 更新当前值
    variable.update(
        CURRENT_VALUE=req.value
    )


@http_service
def query_variable_by_dataset(req):
    variables = VariableDao.select_all_by_dataset(req.datasetNo)

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
def query_variables(req):
    result = []
    for dataset_no in req.list:
        # 查询变量集信息
        dataset = VariableDatasetDao.select_by_no(dataset_no)
        if not dataset:
            continue

        # 查询变量列表
        variables = VariableDao.select_all_by_dataset(dataset_no)

        for variable in variables:
            result.append({
                'datasetNo': dataset.DATASET_NO,
                'datasetName': dataset.DATASET_NAME,
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
    dataset = VariableDatasetDao.select_by_no(req.datasetNo)
    check_exists(dataset, '变量集不存在')

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
    # 批量删除变量
    VariableDao.delete_in_no(req.list)


@http_service
@transactional
def duplicate_variable_dataset(req):
    # 查询变量集
    dataset = VariableDatasetDao.select_by_no(req.datasetNo)
    check_exists(dataset, '变量集不存在')

    # 复制变量集
    dataset_no = new_id()
    TVariableDataset.insert(
        WORKSPACE_NO=dataset.WORKSPACE_NO,
        DATASET_NO=dataset_no,
        DATASET_NAME=dataset.DATASET_NAME + ' copy',
        DATASET_TYPE=dataset.DATASET_TYPE,
        DATASET_DESC=dataset.DATASET_DESC,
        WEIGHT=dataset.WEIGHT
    )

    # 复制变量
    variables = VariableDao.select_all_by_dataset(req.datasetNo)
    for variable in variables:
        TVariable.insert(
            DATASET_NO=dataset_no,
            VAR_NO=new_id(),
            VAR_NAME=variable.VAR_NAME,
            VAR_DESC=variable.VAR_DESC,
            INITIAL_VALUE=variable.INITIAL_VALUE,
            CURRENT_VALUE=variable.CURRENT_VALUE,
            ENABLED=True
        )

    return {'datasetNo': dataset_no}


@http_service
@transactional
def copy_variable_dataset_to_workspace(req):
    # 查询变量集
    dataset = VariableDatasetDao.select_by_no(req.datasetNo)
    check_exists(dataset, '变量集不存在')

    # 复制变量集
    dataset_no = new_id()
    TVariableDataset.insert(
        WORKSPACE_NO=req.workspaceNo,
        DATASET_NO=dataset_no,
        DATASET_NAME=dataset.DATASET_NAME + ' copy',
        DATASET_TYPE=dataset.DATASET_TYPE,
        DATASET_DESC=dataset.DATASET_DESC,
        WEIGHT=dataset.WEIGHT
    )

    # 复制变量
    variables = VariableDao.select_all_by_dataset(req.datasetNo)
    for variable in variables:
        TVariable.insert(
            DATASET_NO=dataset_no,
            VAR_NO=new_id(),
            VAR_NAME=variable.VAR_NAME,
            VAR_DESC=variable.VAR_DESC,
            INITIAL_VALUE=variable.INITIAL_VALUE,
            CURRENT_VALUE=variable.CURRENT_VALUE,
            ENABLED=True
        )

    return {'datasetNo': dataset_no}


@http_service
@transactional
def move_variable_dataset_to_workspace(req):
    # 查询变量集
    dataset = VariableDatasetDao.select_by_no(req.datasetNo)
    check_exists(dataset, '变量集不存在')

    dataset.update(WORKSPACE_NO=req.workspaceNo)
