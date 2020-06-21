create table USER
(
    ID           int auto_increment primary key comment '表ID',
    VERSION      int(8)       not null default 0 comment '版本号',
    DEL_STATE    tinyint(2)   not null default 0 comment '数据状态',
    USER_NO      varchar(32)  not null comment '用户编号',
    USER_NAME    varchar(255) not null comment '用户名称',
    STATE        varchar(32)  not null comment '用户状态(ENABLE启用, CLOSE禁用)',
    MOBILE_NO    varchar(16)  null comment '手机号',
    EMAIL        varchar(255) null comment '邮箱',
    REMARK       varchar(64)  null comment '备注',
    CREATED_BY   varchar(64)  not null comment '创建人',
    CREATED_TIME timestamp    not null default CURRENT_TIMESTAMP comment '创建时间',
    UPDATED_BY   varchar(64)  not null comment '更新人',
    UPDATED_TIME timestamp    not null default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP comment '更新时间'
) comment ='用户表';


create table USER_LOGIN_INFO
(
    ID           int auto_increment primary key comment '表ID',
    VERSION      int(8)      not null default 0 comment '版本号',
    DEL_STATE    tinyint(2)  not null default 0 comment '数据状态',
    USER_NO      varchar(32) not null comment '用户编号',
    LOGIN_NAME   varchar(64) not null comment '登录账号',
    LOGIN_TYPE   varchar(32) not null comment '登陆类型(MOBILE:手机号,EMAIL:邮箱,ACCOUNT:账号)',
    REMARK       varchar(64) null comment '备注',
    CREATED_BY   varchar(64) not null comment '创建人',
    CREATED_TIME timestamp   not null default CURRENT_TIMESTAMP comment '创建时间',
    UPDATED_BY   varchar(64) not null comment '更新人',
    UPDATED_TIME timestamp   not null default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP comment '更新时间'
) comment ='用户登陆号表';


create table USER_LOGIN_LOG
(
    ID           int auto_increment primary key comment '表ID',
    VERSION      int(8)      not null default 0 comment '版本号',
    DEL_STATE    tinyint(2)  not null default 0 comment '数据状态',
    USER_NO      varchar(32) not null comment '用户编号',
    LOGIN_NAME   varchar(64) not null comment '登录账号',
    LOGIN_TYPE   varchar(32) not null comment '登陆类型(MOBILE:手机号, EMAIL:邮箱, ACCOUNT:账号)',
    IP           varchar(64) null comment 'IP地址',
    REMARK       varchar(64) null comment '备注',
    CREATED_BY   varchar(64) not null comment '创建人',
    CREATED_TIME timestamp   not null default CURRENT_TIMESTAMP comment '创建时间',
    UPDATED_BY   varchar(64) not null comment '更新人',
    UPDATED_TIME timestamp   not null default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP comment '更新时间'
) comment ='用户登陆日志表';


create table USER_PASSWORD
(
    ID                int auto_increment primary key comment '表ID',
    VERSION           int(8)       not null default 0 comment '版本号',
    DEL_STATE         tinyint(2)   not null default 0 comment '数据状态',
    USER_NO           varchar(32)  not null comment '用户编号',
    PASSWORD          varchar(256) not null comment '密码',
    PASSWORD_TYPE     varchar(16)  not null comment '密码类型(LOGIN:登录密码)',
    LAST_SUCCESS_TIME timestamp    null comment '最后一次密码校验成功时间',
    LAST_ERROR_TIME   timestamp    null comment '最后一次密码校验错误时间',
    ERROR_TIMES       int(2)       null comment '密码错误次数',
    UNLOCK_TIME       timestamp    null comment '解锁时间',
    CREATE_TYPE       varchar(16)  not null comment '密码创建类型(CUSTOMER:客户设置, SYSTEM:系统生成)',
    REMARK            varchar(64)  null comment '备注',
    CREATED_BY        varchar(64)  not null comment '创建人',
    CREATED_TIME      timestamp    not null default CURRENT_TIMESTAMP comment '创建时间',
    UPDATED_BY        varchar(64)  not null comment '更新人',
    UPDATED_TIME      timestamp    not null default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP comment '更新时间',
    unique (USER_NO, PASSWORD_TYPE)
) comment ='用户密码表';


create table USER_PASSWORD_KEY
(
    ID            int auto_increment primary key comment '表ID',
    VERSION       int(8)       not null default 0 comment '版本号',
    DEL_STATE     tinyint(2)   not null default 0 comment '数据状态',
    USER_NO       varchar(32)  not null comment '用户编号',
    PASSWORD_KEY  varchar(128) not null comment 'RSA公钥',
    REMARK        varchar(64)  null comment '备注',
    CREATED_BY    varchar(64)  not null comment '创建人',
    CREATED_TIME  timestamp    not null default CURRENT_TIMESTAMP comment '创建时间',
    UPDATED_BY    varchar(64)  not null comment '更新人',
    UPDATED_TIME  timestamp    not null default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP comment '更新时间'
) comment ='用户密码公钥表';

create table USER_ACCESS_TOKEN
(
    ID           int auto_increment primary key comment '表ID',
    VERSION      int(8)       not null default 0 comment '版本号',
    DEL_STATE    tinyint(2)   not null default 0 comment '数据状态',
    USER_NO      varchar(32)  not null comment '用户编号',
    LOGIN_NAME   varchar(64)  not null comment '登录账号',
    ACCESS_TOKEN varchar(512) not null comment '令牌',
    EXPIRE_IN    timestamp    not null comment '令牌到期时间',
    STATE        tinyint(2)   not null default 0 comment '令牌状态',
    DEVICE_ID    varchar(64)  null comment '设备ID',
    APP_ID       varchar(64)  null comment '应用ID',
    REMARK       varchar(64)  null comment '备注',
    CREATED_BY   varchar(64)  not null comment '创建人',
    CREATED_TIME timestamp    not null default CURRENT_TIMESTAMP comment '创建时间',
    UPDATED_BY   varchar(64)  not null comment '更新人',
    UPDATED_TIME timestamp    not null default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP comment '更新时间'
) comment ='用户认证令牌表';


create table SYSTEM_OPERATION_LOG
(
    ID             int auto_increment primary key comment '表ID',
    VERSION        int(8)        not null default 0 comment '版本号',
    DEL_STATE      tinyint(2)    not null default 0 comment '数据状态',
    LOG_NO         varchar(32)   not null comment '日志编号',
    USER_NO        varchar(32)   not null comment '用户编号',
    LOGIN_NAME     varchar(64)   not null comment '登录账号',
    CONTENT        varchar(512)  not null comment '操作内容',
    OPT_TYPE       int(2)        not null comment '操作类型(1:登录, 2:新增, 3:删除, 4:修改, 5:查询)',
    IP             varchar(64)   null comment 'IP地址',
    INPUT_PARAMS   varchar(4096) null comment '输入参数',
    OUTPUT_PARAMS  varchar(4096) null comment '输出参数',
    EXCEPTION_MSG  varchar(4096) null comment '异常信息',
    REQ_TIME       timestamp     null comment '请求时间',
    RES_TIME       timestamp     null comment '响应时间',
    TIME_CONSUMING int(7)        null comment '耗时(ms)',
    REMARK         varchar(64)   null comment '备注',
    CREATED_BY     varchar(64)   not null comment '创建人',
    CREATED_TIME   timestamp     not null default CURRENT_TIMESTAMP comment '创建时间',
    UPDATED_BY     varchar(64)   not null comment '更新人',
    UPDATED_TIME   timestamp     not null default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP comment '更新时间'
) comment ='操作日志记录表';

