#!/usr/bin/ python3
# @File    : notice_robot_dao.py
# @Time    : 2022-05-07 22:32:45
# @Author  : Kelvin.Ye
from app.modules.public.model import TNoticeRobot


def select_first(**kwargs) -> TNoticeRobot:
    return TNoticeRobot.filter_by(**kwargs).first()


def select_by_no(robot_no) -> TNoticeRobot:
    return TNoticeRobot.filter_by(ROBOT_NO=robot_no).first()


def select_by_name(robot_name) -> TNoticeRobot:
    return TNoticeRobot.filter_by(ROBOT_NAME=robot_name).first()


def select_by_name_and_type(robot_name, robot_type) -> TNoticeRobot:
    return TNoticeRobot.filter_by(ROBOT_NAME=robot_name, ROBOT_TYPE=robot_type).first()
