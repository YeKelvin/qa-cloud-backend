#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : snowflake_util
# @Time    : 2020/6/17 13:55
# @Author  : Kelvin.Ye
import time


"""
Snowflake是Twitter提出来的一个算法，其目的是生成一个64bit的整数:
-  1bit: 符号位，一般不做处理
- 41bit: 时间戳位，可以记录69年
- 10bit: 机器ID位，可以记录1024台机器，一般前5位代表数据中心，后面5位代表某个数据中心的机器ID
- 12bit: 循环位，用来对同一毫秒之内产生不同的ID，12位最多可以记录4095个，也就是在同一个机器同一毫秒最多记录4095个，多余的需要进行等待下一毫秒
"""

"""
配置文件中添加以下配置项:
DATACENTER_ID = 0   # 数据中心ID
WORKER_ID = 0       # 机器ID
SEQUENCE = 0        # 序列号
"""


# 64位ID的位数划分
DATACENTER_ID_BITS = 5
WORKER_ID_BITS = 5
SEQUENCE_BITS = 12

# 最大取值
MAX_DATACENTER_ID = -1 ^ (-1 << DATACENTER_ID_BITS)
MAX_WORKER_ID = -1 ^ (-1 << WORKER_ID_BITS)  # 2**5-1 0b11111

# 移位偏移值
DATACENTER_ID_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS
WOKER_ID_SHIFT = SEQUENCE_BITS
TIMESTAMP_LEFT_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS + DATACENTER_ID_BITS

# 序号循环掩码
SEQUENCE_MASK = -1 ^ (-1 << SEQUENCE_BITS)

# Twitter元年时间戳
TWEPOCH = 1288834974657


class InvalidSystemClock(Exception):
    """时钟回拨异常"""
    pass


class IdWorker:
    def __init__(self, datacenter_id, worker_id, sequence=0):
        """

        Args:
            datacenter_id:  数据中心ID
            worker_id:      机器ID
            sequence:       序号号
        """
        # sanity check
        if worker_id > MAX_WORKER_ID or worker_id < 0:
            raise ValueError('worker_id值越界')

        if datacenter_id > MAX_DATACENTER_ID or datacenter_id < 0:
            raise ValueError('datacenter_id值越界')

        self.worker_id = worker_id
        self.datacenter_id = datacenter_id
        self.sequence = sequence
        self.last_timestamp = -1  # 上次计算的时间戳

    def new_id(self):
        """获取新ID"""
        timestamp = int(time.time() * 1000)

        # 时钟回拨
        # 雪花算法需要是强依赖时间，如果时间发生回拨，有可能会生成重复的ID
        # 用当前时间和上一次的时间进行判断，如果当前时间小于上一次的时间那么就发生了时间回拨，直接抛出异常
        if timestamp < self.last_timestamp:
            raise InvalidSystemClock(f'clock is moving backwards. Rejecting requests until {self.last_timestamp}')

        if timestamp == self.last_timestamp:
            self.sequence = (self.sequence + 1) & SEQUENCE_MASK
            if self.sequence == 0:
                timestamp = self.__wait_until_next_millis()
        else:
            self.sequence = 0

        self.last_timestamp = timestamp

        return ((timestamp - TWEPOCH) << TIMESTAMP_LEFT_SHIFT) | (self.datacenter_id << DATACENTER_ID_SHIFT) | (self.worker_id << WOKER_ID_SHIFT) | self.sequence

    def __wait_until_next_millis(self):
        """等待到下一毫秒"""
        timestamp = int(time.time() * 1000)
        while timestamp <= self.last_timestamp:
            timestamp = int(time.time() * 1000)
        return timestamp


if __name__ == '__main__':
    worker = IdWorker(1, 2, 0)
    print(worker.new_id())
