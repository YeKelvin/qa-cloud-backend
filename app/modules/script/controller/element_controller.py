#!/usr/bin/ python3
# @File    : element_controller.py
# @Time    : 2020/3/13 16:58
# @Author  : Kelvin.Ye
from app.modules.script.controller import blueprint
from app.modules.script.enum import PasteType
from app.modules.script.service import element_service as service
from app.tools.parser import Argument
from app.tools.parser import JsonParser
from app.tools.require import require_login
from app.tools.require import require_permission


@blueprint.get('/element/list')
@require_login
@require_permission('QUERY_ELEMENT')
def query_element_list():
    """分页查询元素列表"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('workspaceName'),
        Argument('elementNo'),
        Argument('elementName'),
        Argument('elementDesc'),
        Argument('elementType'),
        Argument('elementClass'),
        Argument('enabled'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空'),
    ).parse()
    return service.query_element_list(req)


@blueprint.get('/element/all')
@require_login
@require_permission('QUERY_ELEMENT')
def query_element_all():
    """查询全部元素"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('elementType'),
        Argument('elementClass'),
        Argument('enabled')
    ).parse()
    return service.query_element_all(req)


@blueprint.get('/element/all/with/children')
@require_login
@require_permission('QUERY_ELEMENT')
def query_element_all_with_children():
    """查询全部元素及其子代"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('elementType'),
        Argument('elementClass'),
        Argument('childType'),
        Argument('childClass'),
        Argument('enabled')
    ).parse()
    return service.query_element_all_with_children(req)


@blueprint.get('/element/info')
@require_login
@require_permission('QUERY_ELEMENT')
def query_element_info():
    """查询元素信息"""
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')
    ).parse()
    return service.query_element_info(req)


@blueprint.get('/element/children')
@require_login
@require_permission('QUERY_ELEMENT')
def query_element_tree():
    """查询元素子代"""
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空'),
        Argument('depth', type=bool, required=True, default=True),
    ).parse()
    return service.query_element_tree(req)


@blueprint.get('/element/tree/by/roots')
@require_login
@require_permission('QUERY_ELEMENT')
def query_element_tree_by_roots():
    """根据编号列表批量查询子代元素"""
    req = JsonParser(
        Argument('roots', type=list, required=True, nullable=False, help='元素编号列表不能为空'),
        Argument('depth', type=bool, required=True, default=True),
    ).parse()
    return service.query_element_tree_by_roots(req)


@blueprint.post('/element')
@require_login
@require_permission('CREATE_ELEMENT')
def create_element():
    """新增根元素"""
    req = JsonParser(
        Argument('elementName', required=True, nullable=False, help='元素名称不能为空'),
        Argument('elementDesc'),
        Argument('elementType', required=True, nullable=False, help='元素类型不能为空'),
        Argument('elementClass', required=True, nullable=False, help='元素类不能为空'),
        Argument('elementAttrs', type=dict),
        Argument('elementProps', type=dict),
        Argument('elementCompos', type=dict)
    ).parse()
    return service.create_element(req)


@blueprint.post('/element/child')
@require_login
@require_permission('CREATE_ELEMENT')
def create_element_child():
    """新增子元素"""
    req = JsonParser(
        Argument('rootNo', required=True, nullable=False, help='根元素编号不能为空'),
        Argument('parentNo', required=True, nullable=False, help='父元素编号不能为空'),
        Argument('elementName', required=True, nullable=False, help='元素名称不能为空'),
        Argument('elementDesc'),
        Argument('elementType', required=True, nullable=False, help='元素类型不能为空'),
        Argument('elementClass', required=True, nullable=False, help='元素类不能为空'),
        Argument('elementAttrs', type=dict),
        Argument('elementProps', type=dict),
        Argument('elementCompos', type=dict)
    ).parse()
    return service.create_element_child(req)


@blueprint.put('/element')
@require_login
@require_permission('MODIFY_ELEMENT')
def modify_element():
    """修改元素"""
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空'),
        Argument('elementName'),
        Argument('elementDesc'),
        Argument('elementAttrs', type=dict),
        Argument('elementProps', type=dict),
        Argument('elementCompos', type=dict)
    ).parse()
    return service.modify_element(req)


@blueprint.delete('/element')
@require_login
@require_permission('REMOVE_ELEMENT')
def remove_element():
    """删除元素"""
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')
    ).parse()
    return service.remove_element(req)


@blueprint.put('/element/enable')
@require_login
@require_permission('MODIFY_ELEMENT')
def enable_element():
    """启用元素"""
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')
    ).parse()
    return service.enable_element(req)


@blueprint.put('/element/disable')
@require_login
@require_permission('MODIFY_ELEMENT')
def disable_element():
    """禁用元素"""
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')
    ).parse()
    return service.disable_element(req)


@blueprint.put('/element/skip')
@require_login
@require_permission('MODIFY_ELEMENT')
def skip_element():
    """跳过元素"""
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')
    ).parse()
    return service.skip_element(req)


@blueprint.put('/element/state/toggle')
@require_login
@require_permission('MODIFY_ELEMENT')
def toggle_element_state():
    """切换元素状态"""
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')
    ).parse()
    return service.toggle_element_state(req)


@blueprint.post('/element/move')
@require_login
@require_permission('MOVE_ELEMENT')
def move_element():
    """移动元素"""
    req = JsonParser(
        Argument('sourceNo', required=True, nullable=False, help='Source元素编号不能为空'),
        Argument('targetIndex', type=int, required=True, nullable=False, help='Target元素序号不能为空'),
        Argument('targetRootNo', required=True, nullable=False, help='Target根元素编号不能为空'),
        Argument('targetParentNo', required=True, nullable=False, help='Target父元素编号不能为空')
    ).parse()
    return service.move_element(req)


@blueprint.post('/element/duplicate')
@require_login
@require_permission('COPY_ELEMENT')
def duplicate_element():
    """复制元素及其子代"""
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')
    ).parse()
    return service.duplicate_element(req)


@blueprint.post('/element/paste')
@require_login
@require_permission('PASTE_ELEMENT')
def paste_element():
    """剪贴元素"""
    req = JsonParser(
        Argument('sourceNo', required=True, nullable=False, help='Source元素编号不能为空'),
        Argument('targetNo', required=True, nullable=False, help='Target元素编号不能为空'),
        Argument('pasteType', required=True, nullable=False, enum=PasteType, help='剪贴类型不能为空')
    ).parse()
    return service.paste_element(req)


@blueprint.get('/element/components')
@require_login
@require_permission('QUERY_ELEMENT')
def query_element_components():
    """查询元素组件"""
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')
    ).parse()
    return service.query_element_components(req)


@blueprint.post('/element/copy/to/workspace')
@require_login
@require_permission('COPY_ELEMENT')
def copy_element_to_workspace():
    """复制集合到指定空间"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='空间编号不能为空'),
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')
    ).parse()
    return service.copy_element_to_workspace(req)


@blueprint.post('/element/move/to/workspace')
@require_login
@require_permission('MOVE_ELEMENT')
def move_element_to_workspace():
    """移动集合到指定空间"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='空间编号不能为空'),
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')
    ).parse()
    return service.move_element_to_workspace(req)


@blueprint.get('/element/config/database/all')
@require_login
@require_permission('QUERY_ELEMENT')
def query_database_config_all():
    """查询全部数据库配置"""
    req = JsonParser(
        Argument('workspaceNo')
    ).parse()
    return service.query_database_config_all(req)


@blueprint.get('/element/config/httpheader/template/all')
@require_login
@require_permission('QUERY_ELEMENT')
def query_httpheader_template_all():
    """查询全部HTTP请求头模板"""
    req = JsonParser(
        Argument('workspaceNo')
    ).parse()
    return service.query_httpheader_template_all(req)


@blueprint.get('/element/config/httpheader/all/by-template')
@require_login
@require_permission('QUERY_ELEMENT')
def query_httpheader_all_by_template():
    """根据列表批量查询请求头"""
    req = JsonParser(
        Argument('templates', type=list, required=True, nullable=False, help='模板编号数组不能为空')
    ).parse()
    return service.query_httpheader_all_by_template(req)
