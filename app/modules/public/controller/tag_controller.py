#!/usr/bin/ python3
# @File    : tag_controller.py
# @Time    : 2021-08-17 11:00:49
# @Author  : Kelvin.Ye
from app.modules.public.controller import blueprint
from app.modules.public.service import tag_service as service
from app.tools.decorators.require import require_login
from app.tools.decorators.require import require_permission
from app.tools.parser import Argument
from app.tools.parser import JsonParser


@blueprint.get('/tag/list')
@require_login
@require_permission('QUERY_TAG')
def query_tag_list():
    """分页查询标签列表"""
    req = JsonParser(
        Argument('tagNo'),
        Argument('tagName'),
        Argument('tagDesc'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空'),
    ).parse()
    return service.query_tag_list(req)


@blueprint.get('/tag/all')
@require_login
@require_permission('QUERY_TAG')
def query_tag_all():
    """查询全部标签"""
    return service.query_tag_all()


@blueprint.post('/tag')
@require_login
@require_permission('CREATE_TAG')
def create_tag():
    """新增标签"""
    req = JsonParser(
        Argument('tagName', required=True, nullable=False, help='标签名称不能为空'),
        Argument('tagDesc'),
    ).parse()
    return service.create_tag(req)


@blueprint.put('/tag')
@require_login
@require_permission('MODIFY_TAG')
def modify_tag():
    """修改标签"""
    req = JsonParser(
        Argument('tagNo', required=True, nullable=False, help='标签编号不能为空'),
        Argument('tagName', required=True, nullable=False, help='标签名称不能为空'),
        Argument('tagDesc'),
    ).parse()
    return service.modify_tag(req)


@blueprint.delete('/tag')
@require_login
@require_permission('REMOVE_TAG')
def remove_tag():
    """删除标签"""
    req = JsonParser(
        Argument('tagNo', required=True, nullable=False, help='标签编号不能为空'),
    ).parse()
    return service.remove_tag(req)
