#!/usr/bin/ python3
# @File    : config.py
# @Time    : 2021-11-03 22:45:55
# @Author  : Kelvin.Ye
import os
import tomllib


# 项目路径
PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
# 配置文件路径
if 'APP_CONFIG_FILE' not in os.environ:
    APP_CONFIG_FILE = os.path.join(PROJECT_PATH, 'config.toml')
else:
    APP_CONFIG_FILE = os.environ.get('APP_CONFIG_FILE')


# 读取配置文件
with open(APP_CONFIG_FILE, encoding='utf-8') as f:
    CONFIGS = tomllib.loads(''.join(f.readlines()))


# 配置项
# 服务相关配置
BASE_URL = CONFIGS['service']['baseurl']

# 日志相关配置
LOG_FILE = CONFIGS['log']['file'].replace('.log', '')
LOG_LEVEL = CONFIGS['log']['level']

# 数据库相关配置
DATABASE_TYPE = CONFIGS['database']['type']
DB_URL = CONFIGS['database']['url']

# JWT相关配置
JWT_ISSUER = CONFIGS['jwt']['issuer']
JWT_SECRET_KEY = CONFIGS['jwt']['secret_key']
JWT_EXPIRE_TIME = CONFIGS['jwt']['expire_time']

# 雪花算法相关配置
SNOWFLAKE_DATACENTER_ID = CONFIGS['snowflake']['datacenter_id']
SNOWFLAKE_WORKER_ID = CONFIGS['snowflake']['worker_id']
SNOWFLAKE_SEQUENCE = CONFIGS['snowflake']['sequence']

# 线程相关配置
THREAD_EXECUTOR_WORKERS_MAX = int(CONFIGS['thread']['executor']['max_workers'])

# 定时任务相关配置
SCHEDULE_JOB_INSTANCES_MAX = int(CONFIGS['schedule']['job']['max_instances'])

# 企业登录API
SSO_ENTERPRISE_URL = CONFIGS['sso']['enterprise']['url']
