#!/usr/bin/ python3
# @File    : notification_robot_dao.py
# @Time    : 2022-05-07 22:32:45
# @Author  : Kelvin.Ye
from app.public.model import TNotificationRobot


def select_first(**kwargs) -> TNotificationRobot:
    return TNotificationRobot.filter_by(**kwargs).first()


def select_by_no(robot_no) -> TNotificationRobot:
    return TNotificationRobot.filter_by(ROBOT_NO=robot_no).first()


def select_by_name(robot_name) -> TNotificationRobot:
    return TNotificationRobot.filter_by(ROBOT_NAME=robot_name).first()


def select_by_name_and_type(robot_name, robot_type) -> TNotificationRobot:
    return TNotificationRobot.filter_by(ROBOT_NAME=robot_name, ROBOT_TYPE=robot_type).first()
