#!/usr/bin python3
# @File    : history_service.py
# @Time    : 2023-10-08 15:51:04
# @Author  : Kelvin.Ye
from flask import request
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import union_all
from sqlalchemy.orm import aliased

from app.database import db_execute
from app.modules.public.dao import workspace_dao
from app.modules.script.dao import test_element_dao
from app.modules.script.enum import is_collection
from app.modules.script.enum import is_sampler
from app.modules.script.enum import is_worker
from app.modules.script.model import TElementChangelog
from app.modules.script.model import TTestElement
from app.modules.usercenter.model import TUser
from app.tools.exceptions import ServiceError
from app.tools.service import http_service


TParentElement: TTestElement = aliased(TTestElement)


@http_service
def query_element_changelog_list(req):
    if element := test_element_dao.select_by_no(req.elementNo):
        if is_collection(element):
            stmt = get_changelog_stmt_by_collection(req.elementNo)
            total = count_changelog_by_collection(req.elementNo)
        elif is_worker(element):
            stmt = get_changelog_stmt_by_testcase(req.elementNo)
            total = count_changelog_by_testcase(req.elementNo)
        elif is_sampler(element):
            stmt = get_changelog_stmt_by_sampler(req.elementNo)
            total = count_changelog_by_sampler(req.elementNo)
        else:
            raise ServiceError('暂不支持的元素类型')
    else:
        workspace_no = request.headers.get('x-workspace-no')
        if not workspace_no:
            raise ServiceError('暂不支持的元素类型')
        stmt = get_changelog_stmt_by_workspace(workspace_no)
        total = count_changelog_by_workspace(workspace_no)

    results = db_execute(
        stmt
        .order_by(
            TElementChangelog.CREATED_TIME.desc()
            if req.order == 'desc'
            else TElementChangelog.CREATED_TIME.asc()
        )
        .offset((int(req.page) - 1) * int(req.pageSize))
        .limit(int(req.pageSize))
    ).all()

    data = []
    for entity in results:
        if req.elementNo and entity.ELEMENT_NO == req.elementNo and entity.OPERATION_TYPE in ['INSERT', 'COPY']:
            continue
        data.append({
            'changelogNo': entity.OPERATION_TIME.strftime('%Y%m%d%H:%M:%S.%f'),
            'parentNo': entity.PARENT_NO,
            'parentName': entity.PARENT_NAME,
            'elementNo': entity.ELEMENT_NO,
            'elementName': entity.ELEMENT_NAME,
            'propName': entity.PROP_NAME,
            'attrName': entity.ATTR_NAME,
            'oldValue': entity.OLD_VALUE,
            'newValue': entity.NEW_VALUE,
            'sourceNo': entity.SOURCE_NO,
            'targetNo': entity.TARGET_NO,
            'sourceName': (
                get_element_name(entity.SOURCE_NO)
                if entity.OPERATION_TYPE != 'TRANSFER'
                else get_workspace_name(entity.SOURCE_NO)
            ),
            'targetName': (
                get_element_name(entity.TARGET_NO)
                if entity.OPERATION_TYPE != 'TRANSFER'
                else get_workspace_name(entity.SOURCE_NO)
            ),
            'sourceIndex': entity.SOURCE_INDEX,
            'targetIndex': entity.TARGET_INDEX,
            'operationBy': entity.USER_NAME,
            'operationTime':entity.OPERATION_TIME.strftime('%Y-%m-%d %H:%M:%S'),
            'operationType':entity.OPERATION_TYPE
        })

    return {'data': data, 'total': total}


def get_element_name(element_no):
    if not element_no:
        return
    if element := test_element_dao.select_by_no(element_no):
        return element.ELEMENT_NAME
    else:
        return


def get_workspace_name(workspace_no):
    if not workspace_no:
        return
    if workspace := workspace_dao.select_by_no(workspace_no):
        return workspace.WORKSPACE_NAME
    else:
        return


def get_changelog_stmt_by_workspace(workspace_no):
    stmt = (
        select(
            TElementChangelog,
            TUser.USER_NAME,
            TTestElement.ELEMENT_NAME,
            TTestElement.ELEMENT_TYPE,
            TParentElement.ELEMENT_NAME.label('PARENT_NAME')
        )
        .outerjoin(TUser, TUser.USER_NO == TElementChangelog.OPERATION_BY)
        .outerjoin(TTestElement, TTestElement.ELEMENT_NO == TElementChangelog.ELEMENT_NO)
        .outerjoin(TParentElement, TParentElement.ELEMENT_NO == TElementChangelog.PARENT_NO)
        .where(
            TElementChangelog.WORKSPACE_NO == workspace_no,
            TElementChangelog.ROOT_NO is None,
            TElementChangelog.CASE_NO is None,
            TElementChangelog.PARENT_NO is None
        )
    )
    return union_all(stmt)


def count_changelog_by_workspace(workspace_no):
    stmt = (
        select(func.count(TElementChangelog.ID))
        .where(
            TElementChangelog.WORKSPACE_NO == workspace_no,
            TElementChangelog.ROOT_NO is None,
            TElementChangelog.CASE_NO is None,
            TElementChangelog.PARENT_NO is None
        )
    )
    return int(db_execute(stmt).scalar())


def get_changelog_stmt_by_collection(element_no):
    stmt = (
        select(
            TElementChangelog,
            TUser.USER_NAME,
            TTestElement.ELEMENT_NAME,
            TTestElement.ELEMENT_TYPE,
            TParentElement.ELEMENT_NAME.label('PARENT_NAME')
        )
        .outerjoin(TUser, TUser.USER_NO == TElementChangelog.OPERATION_BY)
        .outerjoin(TTestElement, TTestElement.ELEMENT_NO == TElementChangelog.ELEMENT_NO)
        .outerjoin(TParentElement, TParentElement.ELEMENT_NO == TElementChangelog.PARENT_NO)
        .where(
            TElementChangelog.ROOT_NO == element_no
        )
    )
    return union_all(stmt)


def count_changelog_by_collection(element_no):
    stmt = (
        select(func.count(TElementChangelog.ID))
        .where(
            TElementChangelog.ROOT_NO == element_no
        )
    )
    return int(db_execute(stmt).scalar())



def get_changelog_stmt_by_testcase(element_no):
    stmt = (
        select(
            TElementChangelog,
            TUser.USER_NAME,
            TTestElement.ELEMENT_NAME,
            TTestElement.ELEMENT_TYPE,
            TParentElement.ELEMENT_NAME.label('PARENT_NAME')
        )
        .outerjoin(TUser, TUser.USER_NO == TElementChangelog.OPERATION_BY)
        .outerjoin(TTestElement, TTestElement.ELEMENT_NO == TElementChangelog.ELEMENT_NO)
        .outerjoin(TParentElement, TParentElement.ELEMENT_NO == TElementChangelog.PARENT_NO)
        .where(
            TElementChangelog.CASE_NO == element_no
        )
    )
    return union_all(stmt)


def count_changelog_by_testcase(element_no):
    stmt = (
        select(func.count(TElementChangelog.ID))
        .where(
            TElementChangelog.CASE_NO == element_no
        )
    )
    return int(db_execute(stmt).scalar())


def get_changelog_stmt_by_sampler(element_no):
    sampler_stmt = (
        select(
            TElementChangelog,
            TUser.USER_NAME,
            TTestElement.ELEMENT_NAME,
            TTestElement.ELEMENT_TYPE,
            TParentElement.ELEMENT_NAME.label('PARENT_NAME')
        )
        .outerjoin(TUser, TUser.USER_NO == TElementChangelog.OPERATION_BY)
        .outerjoin(TTestElement, TTestElement.ELEMENT_NO == TElementChangelog.ELEMENT_NO)
        .outerjoin(TParentElement, TParentElement.ELEMENT_NO == TElementChangelog.PARENT_NO)
        .where(TElementChangelog.ELEMENT_NO == element_no)
    )
    component_stmt = (
        select(
            TElementChangelog,
            TUser.USER_NAME,
            TTestElement.ELEMENT_NAME,
            TTestElement.ELEMENT_TYPE,
            TParentElement.ELEMENT_NAME.label('PARENT_NAME')
        )
        .outerjoin(TUser, TUser.USER_NO == TElementChangelog.OPERATION_BY)
        .outerjoin(TTestElement, TTestElement.ELEMENT_NO == TElementChangelog.ELEMENT_NO)
        .outerjoin(TParentElement, TParentElement.ELEMENT_NO == TElementChangelog.PARENT_NO)
        .where(TElementChangelog.PARENT_NO == element_no)
    )
    return union_all(sampler_stmt, component_stmt)


def count_changelog_by_sampler(element_no):
    subtable = union_all(
        (
            select(func.count(TElementChangelog.ID).label('count'))
            .where(
                TElementChangelog.ELEMENT_NO == element_no
            )
        ),
        (
            select(func.count(TElementChangelog.ID).label('count'))
            .where(
                TElementChangelog.PARENT_NO == element_no
            )
        )
    )
    stmt = select(func.sum(subtable.c.count)).select_from(subtable)
    return int(db_execute(stmt).scalar())
