#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : report_service.py
# @Time    : 2021/9/22 14:21
# @Author  : Kelvin.Ye
from app.common.decorators.service import http_service
from app.common.validator import check_is_not_blank
from app.script.dao import test_collection_result_dao as TestCollectionResultDao
from app.script.dao import test_group_result_dao as TestGroupResultDao
from app.script.dao import test_sampler_result_dao as TestSamplerResultDao
from app.utils.log_util import get_logger
from app.utils.time_util import microsecond_to_m_s


log = get_logger(__name__)


@http_service
def query_collection_result(req):
    collection_result = TestCollectionResultDao.select_first_by_collectionid(req.collectionId)
    check_is_not_blank(collection_result, 'CollectionResult不存在')
    return {
        'details': {
            'reportNo': collection_result.REPORT_NO,
            'elementNo': collection_result.COLLECTION_NO,
            'collectionId': collection_result.COLLECTION_ID,
            'collectionName': collection_result.COLLECTION_NAME,
            'collectionRemark': collection_result.COLLECTION_REMARK,
            'startTime': collection_result.START_TIME.strftime('%Y-%m-%d %H:%M:%S'),
            'endTime': collection_result.END_TIME.strftime('%Y-%m-%d %H:%M:%S'),
            'elapsedTime': microsecond_to_m_s(collection_result.ELAPSED_TIME),
            'success': collection_result.SUCCESS,
            'successfulGroupsTotal': TestGroupResultDao.count_by_collection_and_success(req.collectionId, True),
            'successfulSamplersTotal': TestSamplerResultDao.count_by_collection_and_success(req.collectionId, True),
            'failedGroupsTotal': TestGroupResultDao.count_by_collection_and_success(req.collectionId, False),
            'failedSamplersTotal': TestSamplerResultDao.count_by_collection_and_success(req.collectionId, False),
            'avgGroupsElapsedTime': microsecond_to_m_s(
                TestGroupResultDao.avg_elapsed_time_by_collection(req.collectionId)
            ),
            'avgSamplersElapsedTime': f'{TestSamplerResultDao.avg_elapsed_time_by_collection(req.collectionId)}ms'
        },
        'children': get_group_result_list(req.collectionId)
    }


@http_service
def query_group_result(req):
    group_result = TestGroupResultDao.select_first_by_group(req.groupId)
    check_is_not_blank(group_result, 'GroupResult不存在')
    return {
        'groupId': group_result.GROUP_ID,
        'groupName': group_result.GROUP_NAME,
        'groupRemark': group_result.GROUP_REMARK,
        'startTime': group_result.START_TIME.strftime('%Y-%m-%d %H:%M:%S'),
        'endTime': group_result.END_TIME.strftime('%Y-%m-%d %H:%M:%S'),
        'elapsedTime': microsecond_to_m_s(group_result.ELAPSED_TIME),
        'success': group_result.SUCCESS,
        'successfulSamplersTotal': TestSamplerResultDao.count_by_group_and_success(req.groupId, True),
        'failedSamplersTotal': TestSamplerResultDao.count_by_group_and_success(req.groupId, False),
        'avgSamplersElapsedTime': f'{TestSamplerResultDao.avg_elapsed_time_by_group(req.groupId)}ms'
    }


@http_service
def query_sampler_result(req):
    sampler_result = TestSamplerResultDao.select_first_by_sampler(req.samplerId)
    check_is_not_blank(sampler_result, 'SamplerResult不存在')
    return {
        'samplerId': sampler_result.SAMPLER_ID,
        'samplerName': sampler_result.SAMPLER_NAME,
        'samplerRemark': sampler_result.SAMPLER_REMARK,
        'startTime': sampler_result.START_TIME.strftime('%Y-%m-%d %H:%M:%S'),
        'endTime': sampler_result.END_TIME.strftime('%Y-%m-%d %H:%M:%S'),
        'elapsedTime': f'{sampler_result.ELAPSED_TIME}ms',
        'success': sampler_result.SUCCESS,
        'requestUrl': sampler_result.REQUEST_URL,
        'requestHeaders': sampler_result.REQUEST_HEADERS,
        'requestData': sampler_result.REQUEST_DATA,
        'responseCode': sampler_result.RESPONSE_CODE,
        'responseHeaders': sampler_result.RESPONSE_HEADERS,
        'responseData': sampler_result.RESPONSE_DATA,
        'errorAssertion': sampler_result.ERROR_ASSERTION
    }


def get_group_result_list(collection_id):
    groups = []
    group_result_list = TestGroupResultDao.select_all_by_collection(collection_id)
    for group_result in group_result_list:
        groups.append({
            'collectionId': group_result.COLLECTION_ID,
            'id': group_result.GROUP_ID,
            'name': group_result.GROUP_NAME,
            'remark': group_result.GROUP_REMARK,
            'startTime': group_result.START_TIME.strftime('%H:%M:%S'),
            'endTime': group_result.END_TIME.strftime('%H:%M:%S'),
            'elapsedTime': microsecond_to_m_s(group_result.ELAPSED_TIME),
            'success': group_result.SUCCESS,
            'children': get_sampler_result_list(group_result.GROUP_ID)
        })
    return groups


def get_sampler_result_list(group_id):
    samplers = []
    sampler_result_list = TestSamplerResultDao.select_all_summary_by_group(group_id)
    for sampler_result in sampler_result_list:
        samplers.append({
            'groupId': sampler_result.GROUP_ID,
            'parentId': None,
            'id': sampler_result.SAMPLER_ID,
            'name': sampler_result.SAMPLER_NAME,
            'remark': sampler_result.SAMPLER_REMARK,
            'startTime': sampler_result.START_TIME.strftime('%H:%M:%S'),
            'endTime': sampler_result.END_TIME.strftime('%H:%M:%S'),
            'elapsedTime': f'{sampler_result.ELAPSED_TIME}ms',
            'success': sampler_result.SUCCESS,
            'children': get_subsampler_result_list(sampler_result.SAMPLER_ID)
        })
    return samplers


def get_subsampler_result_list(parent_id):
    sub_samplers = []
    sub_sampler_result_list = TestSamplerResultDao.select_all_by_parent(parent_id)
    for sub_result in sub_sampler_result_list:
        sub_samplers.append({
            'groupId': sub_result.GROUP_ID,
            'parentId': parent_id,
            'id': sub_result.SAMPLER_ID,
            'name': sub_result.SAMPLER_NAME,
            'remark': sub_result.SAMPLER_REMARK,
            'startTime': sub_result.START_TIME.strftime('%H:%M:%S'),
            'endTime': sub_result.END_TIME.strftime('%H:%M:%S'),
            'elapsedTime': f'{sub_result.ELAPSED_TIME}ms',
            'success': sub_result.SUCCESS,
            'children': get_subsampler_result_list(sub_result.SAMPLER_ID)
        })
    return sub_samplers
