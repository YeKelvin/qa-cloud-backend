create table USER_ACCESS_TOKEN
(
    ID            NUMBER(10) not null primary key COMMENT '主键ID',
    VERSION       NUMBER(8) COMMENT '乐观锁',
    USER_NO       VARCHAR2(32)  not null COMMENT '用户编号',
    LOGIN_NAME    VARCHAR2(64) COMMENT '登录账号',
    REQ_TEXT      VARCHAR2(512) COMMENT '备注',
    DEVICE_ID     VARCHAR2(40) COMMENT '备注',
    ACCESS_TOKEN  VARCHAR2(300) COMMENT '备注',
    EXPIRE_IN     TIMESTAMP(3) COMMENT '备注',
    SERIAL_NUMBER VARCHAR2(32) COMMENT '备注',
    STATUS        NUMBER(3) default 12 COMMENT '备注',
    REMARK        VARCHAR2(40) COMMENT '备注',
    CREATE_BY     VARCHAR2(32) COMMENT '创建人',
    CREATE_TIME   TIMESTAMP(6) default systimestamp COMMENT '创建时间',
    UPDATE_BY     VARCHAR2(32) COMMENT '更新人',
    UPDATE_TIME   TIMESTAMP(6) default systimestamp COMMENT '更新时间'
) COMMENT='用户认证TOKEN表';


create table USER_BASIC_INFO
(
    ID            NUMBER(10)   not null primary key COMMENT '主键ID',
    VERSION       NUMBER(8)    default 0 COMMENT '乐观锁',
    USER_NO       VARCHAR2(32)  not null COMMENT '用户编号',
    USER_NAME     VARCHAR2(255) not null COMMENT '用户名称',
    STATUS        VARCHAR2(32)  not null COMMENT '商户状态(ENABLE启用, CLOSE禁用)',
    MOBILE_NO     VARCHAR2(16) COMMENT '手机号',
    EMAIL         VARCHAR2(255) COMMENT '邮箱',
    REMARK        VARCHAR2(40) COMMENT '备注',
    CREATE_BY     VARCHAR2(32) COMMENT '创建人',
    CREATE_TIME   TIMESTAMP(6) default systimestamp COMMENT '创建时间',
    UPDATE_BY     VARCHAR2(32) COMMENT '更新人',
    UPDATE_TIME   TIMESTAMP(6) default systimestamp COMMENT '更新时间'
) COMMENT='用户基础信息表';


create table USER_LOGIN_INFO
(
    ID            NUMBER(10)   not null primary key COMMENT '主键ID',
    VERSION       NUMBER(8)    not null default 0  COMMENT '乐观锁',
    USER_NO       VARCHAR2(32) not null COMMENT '用户编号',
    LOGIN_NAME    VARCHAR2(64) COMMENT '登录账号',
    LOGIN_TYPE    VARCHAR2(32) COMMENT '备注',
    REMARK        VARCHAR2(40) COMMENT '备注',
    CREATE_BY     VARCHAR2(32) COMMENT '创建人',
    CREATE_TIME   TIMESTAMP(6) default systimestamp COMMENT '创建时间',
    UPDATE_BY     VARCHAR2(32) COMMENT '更新人',
    UPDATE_TIME   TIMESTAMP(6) default systimestamp COMMENT '更新时间'
) COMMENT='用户登陆号表';


create table USER_LOGIN_LOG
(
    ID             NUMBER(10)    not null primary key COMMENT '主键ID',
    VERSION        NUMBER(8)     not null default 10 COMMENT '乐观锁',
    USER_NO        VARCHAR2(32)  not null COMMENT '用户编号',
    LOGIN_NAME     VARCHAR2(64)  not null COMMENT '登录账号',
    IP             VARCHAR2(256) COMMENT 'IP地址',
    REMARK         VARCHAR2(40)  COMMENT '备注',
    CREATE_BY      VARCHAR2(32)  COMMENT '创建人',
    CREATE_TIME    TIMESTAMP(6)  default systimestamp COMMENT '创建时间',
    UPDATE_BY      VARCHAR2(32)  COMMENT '更新人',
    UPDATE_TIME    TIMESTAMP(6)  default systimestamp COMMENT '更新时间'
) COMMENT='用户登陆日志表';


create table USER_PASSWORD
(
    ID                    NUMBER(10)    not null primary key COMMENT '主键ID',
    VERSION               NUMBER(10)    COMMENT '乐观锁',
    USER_NO               VARCHAR2(32)  COMMENT '用户编号',
    PASSWORD              VARCHAR2(256) COMMENT '密码',
    PASSWORD_TYPE         VARCHAR2(16)  COMMENT '密码类型(LOGIN:登录密码, PAY:支付密码)',
    PWD_ERROR_LAST_TIME   TIMESTAMP(6)  COMMENT '最后一次密码校验错误时间',
    PWD_ERROR_TIMES       NUMBER(2)     COMMENT '密码错误次数',
    LAST_SUCCESS_TIME     TIMESTAMP(6)  COMMENT '最后一次密码校验成功实践',
    UNLOCK_TIME           TIMESTAMP(6)  COMMENT '解锁时间',
    PWD_CREATE_TYPE       VARCHAR2(16)  COMMENT '密码创建类型(CUSTOMER:客户设置, SYSTEM:系统生成)',
    REMARK                VARCHAR2(40)  COMMENT '备注',
    CREATE_BY             VARCHAR2(32)  COMMENT '创建人',
    CREATE_TIME           TIMESTAMP(6)  default systimestamp COMMENT '创建时间',
    UPDATE_BY             VARCHAR2(32)  COMMENT '更新人',
    UPDATE_TIME           TIMESTAMP(6)  default systimestamp COMMENT '更新时间'
    unique (OPERATOR_NO, PASSWORD_TYPE)
) COMMENT='用户密码表';

create table USER_PASSWORD_PUBLIC_KEY
(
    ID              NUMBER(10)    not null primary key COMMENT '主键ID',
    VERSION         NUMBER(10)    COMMENT '乐观锁',
    USER_NO         VARCHAR2(32)  COMMENT '用户编号',
    PASSWORD_TYPE   VARCHAR2(16)  COMMENT '密码类型(LOGIN:登录密码, PAY:支付密码)',
    KEY             VARCHAR2(128) COMMENT 'RSA公钥',
    REMARK          VARCHAR2(40)  COMMENT '备注',
    CREATE_BY       VARCHAR2(32)  COMMENT '创建人',
    CREATE_TIME     TIMESTAMP(6)  default systimestamp COMMENT '创建时间',
    UPDATE_BY       VARCHAR2(32)  COMMENT '更新人',
    UPDATE_TIME     TIMESTAMP(6)  default systimestamp COMMENT '更新时间'
) COMMENT='用户密码公钥表';


create table SYSTEM_OPERATION_LOG
(
    ID              NUMBER(10)     COMMENT '主键ID',
    VERSION         NUMBER(8)      default 0 COMMENT '乐观锁',
    LOG_NO          VARCHAR2(20)   not null COMMENT '日志编号',
    USER_NO         VARCHAR2(32)   not null COMMENT '用户编号',
    USER_NAME       VARCHAR2(30)   not null COMMENT '用户名称',
    LOGIN_NAME      VARCHAR2(32)   not null COMMENT '登录账号',
    CONTENT         VARCHAR2(500)  not null COMMENT '操作内容',
    OPT_TYPE        NUMBER(2)      not null COMMENT '操作类型(1:登录, 2:新增, 3:删除, 4:修改, 5:查询)',
    IP              VARCHAR2(50)   COMMENT 'IP地址',
    INPUT_PARAM     VARCHAR2(4000) COMMENT '输入参数',
    OUTPUT_PARAM    VARCHAR2(4000) COMMENT '输出参数',
    EXCEPTION_MSG   VARCHAR2(4000) COMMENT '异常信息',
    REQ_TIME        TIMESTAMP(6)   COMMENT '请求时间',
    RSP_TIME        TIMESTAMP(6)   COMMENT '响应时间',
    TIME_CONSUMING  NUMBER(7)      COMMENT '耗时(ms)',
    REMARK          VARCHAR2(40)   COMMENT '备注',
    CREATE_BY       VARCHAR2(32)   COMMENT '创建人',
    CREATE_TIME     TIMESTAMP(6)   default systimestamp COMMENT '创建时间',
    UPDATE_BY       VARCHAR2(32)   COMMENT '更新人',
    UPDATE_TIME     TIMESTAMP(6)   default systimestamp COMMENT '更新时间'
) COMMENT='操作日志记录表';

