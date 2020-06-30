#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : service.py
# @Time    : 2019/11/14 9:51
# @Author  : Kelvin.Ye
from server.common.number_generator import generate_project_no
from server.librarys.decorators.service import http_service
from server.librarys.request import RequestDTO
from server.librarys.verify import Verify
from server.script.model import TTestProject
from server.utils.log_util import get_logger

log = get_logger(__name__)


@http_service
def query_project_list(req: RequestDTO):
    # 查询条件
    conditions = [TTestProject.DEL_STATE == 0]

    if req.attr.projectNo:
        conditions.append(TTestProject.PROJECT_NO.like(f'%{req.attr.projectNo}%'))
    if req.attr.projectName:
        conditions.append(TTestProject.PROJECT_NAME.like(f'%{req.attr.projectName}%'))
    if req.attr.projectDesc:
        conditions.append(TTestProject.PROJECT_DESC.like(f'%{req.attr.projectDesc}%'))

    pagination = TTestProject.query.filter(
        *conditions).order_by(TTestProject.CREATED_TIME.desc()).paginate(req.attr.page, req.attr.pageSize)

    # 组装数据
    data_set = []
    for item in pagination.items:
        data_set.append({
            'projectNo': item.PROJECT_NO,
            'projectName': item.PROJECT_NAME,
            'projectDesc': item.PROJECT_DESC
        })
    return {'dataSet': data_set, 'totalSize': pagination.total}


@http_service
def query_project_all():
    projects = TTestProject.query_by().order_by(TTestProject.CREATED_TIME.desc()).all()
    result = []
    for project in projects:
        result.append({
            'projectNo': project.PROJECT_NO,
            'projectName': project.PROJECT_NAME,
            'projectDesc': project.PROJECT_DESC
        })
    return result


@http_service
def create_project(req: RequestDTO):
    project = TTestProject.query_by(PROJECT_NAME=req.attr.projectName).first()
    Verify.empty(project, '测试项目已存在')

    TTestProject.create(
        PROJECT_NO=generate_project_no(),
        PROJECT_NAME=req.attr.projectName,
        PROJECT_DESC=req.attr.projectDesc
    )
    return None


@http_service
def modify_project(req: RequestDTO):
    project = TTestProject.query_by(PROJECT_NO=req.attr.projectNo).first()
    Verify.not_empty(project, '测试项目不存在')

    if req.attr.projectName is not None:
        project.PROJECT_NAME = req.attr.projectName
    if req.attr.projectDesc is not None:
        project.PROJECT_DESC = req.attr.projectDesc

    project.save()
    return None


@http_service
def delete_project(req: RequestDTO):
    project = TTestProject.query_by(PROJECT_NO=req.attr.projectNo).first()
    Verify.not_empty(project, '测试项目不存在')

    project.update(DEL_STATE=1)
    return None


@http_service
def add_project_user(req: RequestDTO):
    pass


@http_service
def modify_project_user(req: RequestDTO):
    pass


@http_service
def remove_project_user(req: RequestDTO):
    pass
