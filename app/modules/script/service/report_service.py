#!/usr/bin/ python3
# @File    : report_service.py
# @Time    : 2021/9/22 14:21
# @Author  : Kelvin.Ye
from app.modules.script.dao import test_collection_result_dao as TestCollectionResultDao
from app.modules.script.dao import test_group_result_dao as TestGroupResultDao
from app.modules.script.dao import test_report_dao as TestReportDao
from app.modules.script.dao import test_sampler_result_dao as TestSamplerResultDao
from app.tools.service import http_service
from app.tools.validator import check_exists
from app.utils.time_util import microsecond_to_h_m_s
from app.utils.time_util import microsecond_to_m_s


@http_service
def query_report(req):
    # 查询测试报告
    report = TestReportDao.select_by_no(req.reportNo)
    check_exists(report, error_msg='测试报告不存在')

    # 递归查询脚本结果
    collections = []
    collection_result_list = TestCollectionResultDao.select_all_by_report(report.REPORT_NO)
    for collection_result in collection_result_list:
        collections.append({
            'reportNo': collection_result.REPORT_NO,
            'elementNo': collection_result.COLLECTION_NO,
            'id': collection_result.COLLECTION_ID,
            'name': collection_result.COLLECTION_NAME,
            'remark': collection_result.COLLECTION_REMARK,
            'startTime': collection_result.START_TIME.strftime('%H:%M:%S') if collection_result.START_TIME else 0,
            'endTime': collection_result.END_TIME.strftime('%H:%M:%S') if collection_result.END_TIME else 0,
            'elapsedTime': microsecond_to_m_s(collection_result.ELAPSED_TIME),
            'success': collection_result.SUCCESS,
        })

    return {
        'details': {
            'reportName': report.REPORT_NAME,
            'reportDesc': report.REPORT_DESC,
            'startTime': report.START_TIME.strftime('%Y-%m-%d %H:%M:%S') if report.START_TIME else 0,
            'endTime': report.END_TIME.strftime('%Y-%m-%d %H:%M:%S') if report.END_TIME else 0,
            'elapsedTime': microsecond_to_h_m_s(report.ELAPSED_TIME),
            'successfulCollectionsTotal': TestCollectionResultDao.count_by_report_and_success(report.REPORT_NO, True),
            'successfulGroupsTotal': TestGroupResultDao.count_by_report_and_success(report.REPORT_NO, True),
            'successfulSamplersTotal': TestSamplerResultDao.count_by_report_and_success(report.REPORT_NO, True),
            'failedCollectionsTotal': TestCollectionResultDao.count_by_report_and_success(report.REPORT_NO, False),
            'failedGroupsTotal': TestGroupResultDao.count_by_report_and_success(report.REPORT_NO, False),
            'failedSamplersTotal': TestSamplerResultDao.count_by_report_and_success(report.REPORT_NO, False),
            'avgCollectionsElapsedTime': microsecond_to_m_s(
                TestCollectionResultDao.avg_elapsed_time_by_report(report.REPORT_NO)
            ),
            'avgGroupsElapsedTime': microsecond_to_m_s(
                TestGroupResultDao.avg_elapsed_time_by_report(report.REPORT_NO)
            ),
            'avgSamplersElapsedTime': f'{TestSamplerResultDao.avg_elapsed_time_by_report(report.REPORT_NO)}ms',
        },
        'collections': collections
    }


@http_service
def query_collection_result(req):
    result = TestCollectionResultDao.select_first_by_collectionid(req.collectionId)
    check_exists(result, error_msg='CollectionResult不存在')
    return {
        'details': {
            'reportNo': result.REPORT_NO,
            'elementNo': result.COLLECTION_NO,
            'collectionId': result.COLLECTION_ID,
            'collectionName': result.COLLECTION_NAME,
            'collectionRemark': result.COLLECTION_REMARK,
            'startTime': result.START_TIME.strftime('%Y-%m-%d %H:%M:%S') if result.START_TIME else 0,
            'endTime': result.END_TIME.strftime('%Y-%m-%d %H:%M:%S') if result.END_TIME else 0,
            'elapsedTime': microsecond_to_m_s(result.ELAPSED_TIME),
            'success': result.SUCCESS,
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
    result = TestGroupResultDao.select_first_by_group(req.groupId)
    check_exists(result, error_msg='GroupResult不存在')
    return {
        'groupId': result.GROUP_ID,
        'groupName': result.GROUP_NAME,
        'groupRemark': result.GROUP_REMARK,
        'startTime': result.START_TIME.strftime('%Y-%m-%d %H:%M:%S')if result.START_TIME else 0,
        'endTime': result.END_TIME.strftime('%Y-%m-%d %H:%M:%S') if result.END_TIME else 0,
        'elapsedTime': microsecond_to_m_s(result.ELAPSED_TIME),
        'success': result.SUCCESS,
        'successfulSamplersTotal': TestSamplerResultDao.count_by_group_and_success(req.groupId, True),
        'failedSamplersTotal': TestSamplerResultDao.count_by_group_and_success(req.groupId, False),
        'avgSamplersElapsedTime': f'{TestSamplerResultDao.avg_elapsed_time_by_group(req.groupId)}ms'
    }


@http_service
def query_sampler_result(req):
    result = TestSamplerResultDao.select_first_by_sampler(req.samplerId)
    check_exists(result, error_msg='SamplerResult不存在')
    return {
        'samplerId': result.SAMPLER_ID,
        'samplerName': result.SAMPLER_NAME,
        'samplerRemark': result.SAMPLER_REMARK,
        'startTime': result.START_TIME.strftime('%Y-%m-%d %H:%M:%S') if result.START_TIME else 0,
        'endTime': result.END_TIME.strftime('%Y-%m-%d %H:%M:%S') if result.END_TIME else 0,
        'elapsedTime': f'{result.ELAPSED_TIME}ms',
        'success': result.SUCCESS,
        'retrying': result.RETRYING,
        'requestUrl': result.REQUEST_URL,
        'requestHeaders': result.REQUEST_HEADERS,
        'requestData': result.REQUEST_DATA,
        'responseCode': result.RESPONSE_CODE,
        'responseHeaders': result.RESPONSE_HEADERS,
        'responseData': result.RESPONSE_DATA,
        'failedAssertion': result.FAILED_ASSERTION
    }


def get_group_result_list(collection_id):
    groups = []
    group_result_list = TestGroupResultDao.select_all_by_collection(collection_id)
    for result in group_result_list:
        groups.append({
            'collectionId': result.COLLECTION_ID,
            'id': result.GROUP_ID,
            'name': result.GROUP_NAME,
            'remark': result.GROUP_REMARK,
            'startTime': result.START_TIME.strftime('%H:%M:%S') if result.START_TIME else 0,
            'endTime': result.END_TIME.strftime('%H:%M:%S') if result.END_TIME else 0,
            'elapsedTime': microsecond_to_m_s(result.ELAPSED_TIME),
            'success': result.SUCCESS,
            'children': get_sampler_result_list(result.GROUP_ID)
        })
    return groups


def get_sampler_result_list(group_id):
    samplers = []
    sampler_result_list = TestSamplerResultDao.select_all_summary_by_group(group_id)
    for result in sampler_result_list:
        samplers.append({
            'groupId': result.GROUP_ID,
            'parentId': None,
            'id': result.SAMPLER_ID,
            'name': result.SAMPLER_NAME,
            'remark': result.SAMPLER_REMARK,
            'startTime': result.START_TIME.strftime('%H:%M:%S') if result.START_TIME else 0,
            'endTime': result.END_TIME.strftime('%H:%M:%S') if result.END_TIME else 0,
            'elapsedTime': f'{result.ELAPSED_TIME}ms',
            'success': result.SUCCESS,
            'retrying': result.RETRYING,
            'children': get_subsampler_result_list(result.SAMPLER_ID)
        })
    return samplers


def get_subsampler_result_list(parent_id):
    sub_samplers = []
    sub_sampler_result_list = TestSamplerResultDao.select_all_by_parent(parent_id)
    for result in sub_sampler_result_list:
        sub_samplers.append({
            'groupId': result.GROUP_ID,
            'parentId': parent_id,
            'id': result.SAMPLER_ID,
            'name': result.SAMPLER_NAME,
            'remark': result.SAMPLER_REMARK,
            'startTime': result.START_TIME.strftime('%H:%M:%S') if result.START_TIME else 0,
            'endTime': result.END_TIME.strftime('%H:%M:%S') if result.END_TIME else 0,
            'elapsedTime': f'{result.ELAPSED_TIME}ms',
            'success': result.SUCCESS,
            'retrying': result.RETRYING,
            'children': get_subsampler_result_list(result.SAMPLER_ID)
        })
    return sub_samplers
