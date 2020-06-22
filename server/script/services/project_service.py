#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : service.py
# @Time    : 2019/11/14 9:51
# @Author  : Kelvin.Ye
from server.common.number_generator import generate_project_no
from server.librarys.decorators.service import http_service
from server.librarys.helpers.sqlalchemy_helper import pagination
from server.librarys.request import RequestDTO
from server.librarys.verify import Verify
from server.script.model import TTestProject
from server.utils.log_util import get_logger

log = get_logger(__name__)


@http_service
def query_project_list(req: RequestDTO):
    # 分页
    offset, limit = pagination(req)

    # 查询条件
    conditions = [TTestProject.DEL_STATE == 0]
    if req.attr.projectNo:
        conditions.append(TTestProject.PROJECT_NO.like(f'%{req.attr.projectNo}%'))
    if req.attr.projectName:
        conditions.append(TTestProject.PROJECT_NAME.like(f'%{req.attr.projectName}%'))
    if req.attr.projectDesc:
        conditions.append(TTestProject.PROJECT_DESC.like(f'%{req.attr.projectDesc}%'))

    # 列表总数
    total_size = TTestProject.query.filter(*conditions).count()

    # 列表数据
    projects = TTestProject.query.filter(
        *conditions
    ).order_by(
        TTestProject.CREATED_TIME.desc()
    ).offset(offset).limit(limit).all()

    # 组装响应数据
    data_set = []
    for project in projects:
        data_set.append({
            'projectNo': project.PROJECT_NO,
            'projectName': project.PROJECT_NAME,
            'projectDesc': project.PROJECT_DESC
        })
    return {'dataSet': data_set, 'totalSize': total_size}


@http_service
def query_project_all():
    projects = TTestProject.query.filter_by(DEL_STATE=0).order_by(TTestProject.CREATED_TIME.desc()).all()
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
    project = TTestProject.query.filter_by(PROJECT_NAME=req.attr.projectName, DEL_STATE=0).first()
    Verify.empty(project, '测试项目已存在')

    TTestProject.create(
        PROJECT_NO=generate_project_no(),
        PROJECT_NAME=req.attr.projectName,
        PROJECT_DESC=req.attr.projectDesc
    )
    return None


@http_service
def modify_project(req: RequestDTO):
    project = TTestProject.query.filter_by(PROJECT_NO=req.attr.projectNo, DEL_STATE=0).first()
    Verify.not_empty(project, '测试项目不存在')

    if req.attr.projectName is not None:
        project.PROJECT_NAME = req.attr.projectName
    if req.attr.projectDesc is not None:
        project.PROJECT_DESC = req.attr.projectDesc

    project.save()
    return None


@http_service
def delete_project(req: RequestDTO):
    project = TTestProject.query.filter_by(PROJECT_NO=req.attr.projectNo, DEL_STATE=0).first()
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
