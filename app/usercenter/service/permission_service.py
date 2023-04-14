#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : permission_service.py
# @Time    : 2020/3/17 15:37
# @Author  : Kelvin.Ye
from app.database import dbquery
from app.tools.decorators.service import http_service
from app.usercenter.model import TPermission
from app.usercenter.model import TPermissionModule
from app.usercenter.model import TPermissionObject
from app.utils.sqlalchemy_util import QueryCondition


@http_service
def query_permission_all(req):
    conds = QueryCondition(TPermissionModule, TPermissionObject, TPermission)
    conds.equal(TPermissionModule.MODULE_NO, TPermission.MODULE_NO)
    conds.equal(TPermissionObject.OBJECT_NO, TPermission.OBJECT_NO)
    conds.in_(TPermissionModule.MODULE_CODE, req.moduleCodes)
    conds.in_(TPermissionObject.OBJECT_CODE, req.objectCodes)
    conds.notin_(TPermission.PERMISSION_ACT, req.actExcludes)
    resutls = (
        dbquery(
            TPermissionModule.MODULE_NO,
            TPermissionModule.MODULE_NAME,
            TPermissionModule.MODULE_CODE,
            TPermissionObject.OBJECT_NO,
            TPermissionObject.OBJECT_NAME,
            TPermissionObject.OBJECT_CODE,
            TPermission.PERMISSION_NO,
            TPermission.PERMISSION_NAME,
            TPermission.PERMISSION_DESC,
            TPermission.PERMISSION_CODE,
            TPermission.STATE
        )
        .filter(*conds)
        .order_by(TPermissionModule.MODULE_CODE.asc(), TPermissionObject.OBJECT_CODE.asc())
        .all()
    )
    return [
        {
            'moduleNo': resutl.MODULE_NO,
            'moduleName': resutl.MODULE_NAME,
            'moduleCode': resutl.MODULE_CODE,
            'objectNo': resutl.OBJECT_NO,
            'objectName': resutl.OBJECT_NAME,
            'objectCode': resutl.OBJECT_CODE,
            'permissionNo': resutl.PERMISSION_NO,
            'permissionName': resutl.PERMISSION_NAME,
            'permissionDesc': resutl.PERMISSION_DESC,
            'permissionCode': resutl.PERMISSION_CODE,
            'state': resutl.STATE
        }
        for resutl in resutls
    ]
