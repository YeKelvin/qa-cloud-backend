#!/usr/bin/ python3
# @File    : report_service.py
# @Time    : 2021/9/22 14:21
# @Author  : Kelvin.Ye
from app.modules.script.dao import test_collection_result_dao
from app.modules.script.dao import test_report_dao
from app.modules.script.dao import test_sampler_result_dao
from app.modules.script.dao import test_worker_result_dao
from app.tools.service import http_service
from app.tools.validator import check_exists
from app.utils.time_util import microsecond_to_h_m_s
from app.utils.time_util import microsecond_to_m_s


@http_service
def query_report(req):
    # 查询测试报告
    report = test_report_dao.select_by_no(req.reportNo)
    check_exists(report, error='测试报告不存在')

    # 查询集合结果
    collection_result_list = test_collection_result_dao.select_all_by_report(report.REPORT_NO)
    collections = [
        {
            'reportNo': collection_result.REPORT_NO,
            'elementNo': collection_result.COLLECTION_NO,
            'id': collection_result.COLLECTION_ID,
            'name': collection_result.COLLECTION_NAME,
            'desc': collection_result.COLLECTION_DESC,
            'startTime': collection_result.START_TIME.strftime('%H:%M:%S')
            if collection_result.START_TIME
            else 0,
            'endTime': collection_result.END_TIME.strftime('%H:%M:%S')
            if collection_result.END_TIME
            else 0,
            'elapsedTime': microsecond_to_m_s(collection_result.ELAPSED_TIME),
            'success': collection_result.SUCCESS,
        }
        for collection_result in collection_result_list
    ]

    return {
        'details': {
            'reportName': report.REPORT_NAME,
            'reportDesc': report.REPORT_DESC,
            'startTime': report.START_TIME.strftime('%Y-%m-%d %H:%M:%S') if report.START_TIME else 0,
            'endTime': report.END_TIME.strftime('%Y-%m-%d %H:%M:%S') if report.END_TIME else 0,
            'elapsedTime': microsecond_to_h_m_s(report.ELAPSED_TIME),
            'successfulCollectionTotal':
                test_collection_result_dao.count_by_report_and_success(report.REPORT_NO, True),
            'successfulWorkerTotal':
                test_worker_result_dao.count_by_report_and_success(report.REPORT_NO, True),
            'successfulSamplerTotal':
                test_sampler_result_dao.count_by_report_and_success(report.REPORT_NO, True),
            'failedCollectionTotal':
                test_collection_result_dao.count_by_report_and_success(report.REPORT_NO, False),
            'failedWorkerTotal':
                test_worker_result_dao.count_by_report_and_success(report.REPORT_NO, False),
            'failedSamplerTotal':
                test_sampler_result_dao.count_by_report_and_success(report.REPORT_NO, False),
            'avgCollectionsElapsedTime': microsecond_to_m_s(
                test_collection_result_dao.avg_elapsed_time_by_report(report.REPORT_NO)
            ),
            'avgWorkersElapsedTime': microsecond_to_m_s(
                test_worker_result_dao.avg_elapsed_time_by_report(report.REPORT_NO)
            ),
            'avgSamplersElapsedTime': f'{test_sampler_result_dao.avg_elapsed_time_by_report(report.REPORT_NO)}ms',
        },
        'collections': collections
    }


@http_service
def query_collection_result(req):
    result = test_collection_result_dao.select_first_by_collectionid(req.collectionId)
    check_exists(result, error='集合结果不存在')
    return {
        'details': {
            'reportNo': result.REPORT_NO,
            'elementNo': result.COLLECTION_NO,
            'collectionId': result.COLLECTION_ID,
            'collectionName': result.COLLECTION_NAME,
            'collectionDesc': result.COLLECTION_DESC,
            'startTime': result.START_TIME.strftime('%Y-%m-%d %H:%M:%S') if result.START_TIME else 0,
            'endTime': result.END_TIME.strftime('%Y-%m-%d %H:%M:%S') if result.END_TIME else 0,
            'elapsedTime': microsecond_to_m_s(result.ELAPSED_TIME),
            'success': result.SUCCESS,
            'successfulWorkerTotal': test_worker_result_dao.count_by_collection_and_success(req.collectionId, True),
            'successfulSamplerTotal': test_sampler_result_dao.count_by_collection_and_success(req.collectionId, True),
            'failedWorkerTotal': test_worker_result_dao.count_by_collection_and_success(req.collectionId, False),
            'failedSamplerTotal': test_sampler_result_dao.count_by_collection_and_success(req.collectionId, False),
            'avgWorkersElapsedTime': microsecond_to_m_s(
                test_worker_result_dao.avg_elapsed_time_by_collection(req.collectionId)
            ),
            'avgSamplersElapsedTime': f'{test_sampler_result_dao.avg_elapsed_time_by_collection(req.collectionId)}ms'
        },
        'children': get_worker_result_list(req.collectionId)
    }


@http_service
def query_worker_result(req):
    result = test_worker_result_dao.select_first_by_worker(req.workerId)
    check_exists(result, error='用例结果不存在')
    return {
        'workerId': result.WORKER_ID,
        'workerName': result.WORKER_NAME,
        'workerDesc': result.WORKER_DESC,
        'startTime': result.START_TIME.strftime('%Y-%m-%d %H:%M:%S')if result.START_TIME else 0,
        'endTime': result.END_TIME.strftime('%Y-%m-%d %H:%M:%S') if result.END_TIME else 0,
        'elapsedTime': microsecond_to_m_s(result.ELAPSED_TIME),
        'success': result.SUCCESS,
        'successfulSamplerTotal': test_sampler_result_dao.count_by_worker_and_success(req.workerId, True),
        'failedSamplerTotal': test_sampler_result_dao.count_by_worker_and_success(req.workerId, False),
        'avgSamplersElapsedTime': f'{test_sampler_result_dao.avg_elapsed_time_by_worker(req.workerId)}ms'
    }


@http_service
def query_sampler_result(req):
    result = test_sampler_result_dao.select_first_by_sampler(req.samplerId)
    check_exists(result, error='请求结果不存在')
    return {
        'samplerId': result.SAMPLER_ID,
        'samplerName': result.SAMPLER_NAME,
        'samplerDesc': result.SAMPLER_DESC,
        'startTime': result.START_TIME.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] if result.START_TIME else 0,
        'endTime': result.END_TIME.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] if result.END_TIME else 0,
        'elapsedTime': f'{result.ELAPSED_TIME}ms',
        'success': result.SUCCESS,
        'retrying': result.RETRYING,
        'requestUrl': result.REQUEST_URL,
        'requestHeaders': result.REQUEST_HEADERS,
        'requestData': result.REQUEST_DATA,
        'requestDecoded': result.REQUEST_DECODED,
        'responseCode': result.RESPONSE_CODE,
        'responseHeaders': result.RESPONSE_HEADERS,
        'responseData': result.RESPONSE_DATA,
        'responseDecoded': result.RESPONSE_DECODED,
        'failedAssertion': result.FAILED_ASSERTION
    }


def get_worker_result_list(collection_id):
    worker_result_list = test_worker_result_dao.select_all_by_collection(collection_id)
    return [
        {
            'collectionId': result.COLLECTION_ID,
            'id': result.WORKER_ID,
            'name': result.WORKER_NAME,
            'desc': result.WORKER_DESC,
            'startTime': (
                result.START_TIME.strftime('%H:%M:%S')
                if result.START_TIME
                else 0
            ),
            'endTime': (
                result.END_TIME.strftime('%H:%M:%S')
                if result.END_TIME
                else 0
            ),
            'elapsedTime': microsecond_to_m_s(result.ELAPSED_TIME),
            'success': result.SUCCESS,
            'children': get_sampler_result_list(result.WORKER_ID),
        }
        for result in worker_result_list
    ]


def get_sampler_result_list(worker_id):
    sampler_result_list = test_sampler_result_dao.select_all_summary_by_worker(worker_id)
    return [
        {
            'workerId': result.WORKER_ID,
            'parentId': None,
            'id': result.SAMPLER_ID,
            'name': result.SAMPLER_NAME,
            'desc': result.SAMPLER_DESC,
            'startTime': (
                result.START_TIME.strftime('%H:%M:%S.%f')
                if result.START_TIME
                else 0
            ),
            'endTime': (
                result.END_TIME.strftime('%H:%M:%S.%f')
                if result.END_TIME
                else 0
            ),
            'elapsedTime': f'{result.ELAPSED_TIME}ms',
            'success': result.SUCCESS,
            'retrying': result.RETRYING,
            'children': get_subsampler_result_list(result.SAMPLER_ID),
        }
        for result in sampler_result_list
    ]


def get_subsampler_result_list(parent_id):
    sub_sampler_result_list = test_sampler_result_dao.select_all_by_parent(parent_id)
    return [
        {
            'workerId': result.WORKER_ID,
            'parentId': parent_id,
            'id': result.SAMPLER_ID,
            'name': result.SAMPLER_NAME,
            'desc': result.SAMPLER_DESC,
            'startTime': (
                result.START_TIME.strftime('%H:%M:%S.%f')
                if result.START_TIME
                else 0
            ),
            'endTime': (
                result.END_TIME.strftime('%H:%M:%S.%f')
                if result.END_TIME
                else 0
            ),
            'elapsedTime': f'{result.ELAPSED_TIME}ms',
            'success': result.SUCCESS,
            'retrying': result.RETRYING,
            'children': get_subsampler_result_list(result.SAMPLER_ID),
        }
        for result in sub_sampler_result_list
    ]
