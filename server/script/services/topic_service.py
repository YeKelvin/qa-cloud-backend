#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : topic_service
# @Time    : 2020/3/13 16:56
# @Author  : Kelvin.Ye
from server.common.id_generator import new_id
from server.common.decorators.service import http_service
from server.common.request import RequestDTO
from server.common.validator import assert_blank, assert_not_blank
from server.script.models import TTestTopic
from server.utils.log_util import get_logger

log = get_logger(__name__)


@http_service
def query_topic_list(req: RequestDTO):
    # 查询条件
    conditions = [TTestTopic.DEL_STATE == 0]

    if req.attr.topicNo:
        conditions.append(TTestTopic.TOPIC_NO.like(f'%{req.attr.topicNo}%'))
    if req.attr.topicName:
        conditions.append(TTestTopic.TOPIC_NAME.like(f'%{req.attr.topicName}%'))
    if req.attr.topicDesc:
        conditions.append(TTestTopic.TOPIC_DESC.like(f'%{req.attr.topicDesc}%'))

    pagination = TTestTopic.query.filter(
        *conditions).order_by(TTestTopic.CREATED_TIME.desc()).paginate(req.attr.page, req.attr.pageSize)

    # 组装数据
    data_set = []
    for item in pagination.items:
        data_set.append({
            'topicNo': item.TOPIC_NO,
            'topicName': item.TOPIC_NAME,
            'topicDesc': item.TOPIC_DESC
        })
    return {'dataSet': data_set, 'totalSize': pagination.total}


@http_service
def query_topic_all():
    topics = TTestTopic.query_by().order_by(TTestTopic.CREATED_TIME.desc()).all()
    result = []
    for topic in topics:
        result.append({
            'topicNo': topic.TOPIC_NO,
            'topicName': topic.TOPIC_NAME,
            'topicDesc': topic.TOPIC_DESC
        })
    return result


@http_service
def create_topic(req: RequestDTO):
    topic = TTestTopic.query_by(TOPIC_NAME=req.attr.topicName).first()
    assert_blank(topic, '测试主题已存在')

    TTestTopic.create(
        TOPIC_NO=new_id(),
        TOPIC_NAME=req.attr.topicName,
        TOPIC_DESC=req.attr.topicDesc
    )
    return None


@http_service
def modify_topic(req: RequestDTO):
    topic = TTestTopic.query_by(TOPIC_NO=req.attr.topicNo).first()
    assert_not_blank(topic, '测试主题不存在')

    if req.attr.topicName is not None:
        topic.TOPIC_NAME = req.attr.topicName
    if req.attr.topicDesc is not None:
        topic.TOPIC_DESC = req.attr.topicDesc

    topic.save()
    return None


@http_service
def delete_topic(req: RequestDTO):
    topic = TTestTopic.query_by(TOPIC_NO=req.attr.topicNo).first()
    assert_not_blank(topic, '测试主题不存在')

    topic.update(DEL_STATE=1)
    return None


@http_service
def add_topic_collection(req: RequestDTO):
    pass


@http_service
def modify_topic_collection(req: RequestDTO):
    pass


@http_service
def remove_topic_collection(req: RequestDTO):
    pass
