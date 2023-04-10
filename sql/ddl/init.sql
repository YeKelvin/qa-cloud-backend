------------------------------⬇️ usercenter ⬇️------------------------------
-- 用户表
create table "USER"
(
    "ID"           serial       primary key,
    "USER_NO"      varchar(32)  not null    UNIQUE,
    "USER_NAME"    varchar(128) not null,
    "MOBILE_NO"    varchar(16),
    "EMAIL"        varchar(128),
    "AVATAR"       varchar(256),
    "STATE"        varchar(16)  not null,
    "LOGGED_IN"    boolean      not null,
    "VERSION"      integer      not null,
    "DELETED"      integer      not null,
    "REMARK"       varchar(64),
    "CREATED_BY"   varchar(64),
    "CREATED_TIME" timestamp,
    "UPDATED_BY"   varchar(64),
    "UPDATED_TIME" timestamp
);
comment on column "USER"."ID" is '主键';
comment on column "USER"."USER_NO" is '用户编号';
comment on column "USER"."USER_NAME" is '用户名称';
comment on column "USER"."MOBILE_NO" is '手机号';
comment on column "USER"."EMAIL" is '邮箱';
comment on column "USER"."AVATAR" is '头像URL';
comment on column "USER"."STATE" is '用户状态（ENABLE:启用, DISABLE:禁用）';
comment on column "USER"."LOGGED_IN" is '登录标识';
comment on column "USER"."VERSION" is '版本号';
comment on column "USER"."DELETED" is '删除标识';
comment on column "USER"."REMARK" is '备注';
comment on column "USER"."CREATED_BY" is '创建人';
comment on column "USER"."CREATED_TIME" is '创建时间';
comment on column "USER"."UPDATED_BY" is '更新人';
comment on column "USER"."UPDATED_TIME" is '更新时间';


-- 用户分组表
create table "USER_GROUP"
(
    "ID"           serial      primary key,
    "USER_NO"      varchar(32) not null,
    "GROUP_NO"     varchar(32) not null,
    "VERSION"      integer     not null,
    "DELETED"      integer     not null,
    "REMARK"       varchar(64),
    "CREATED_BY"   varchar(64),
    "CREATED_TIME" timestamp,
    "UPDATED_BY"   varchar(64),
    "UPDATED_TIME" timestamp
);
comment on column "USER_GROUP"."ID" is '主键';
comment on column "USER_GROUP"."USER_NO" is '用户编号';
comment on column "USER_GROUP"."GROUP_NO" is '分组编号';
comment on column "USER_GROUP"."VERSION" is '版本号';
comment on column "USER_GROUP"."DELETED" is '删除标识';
comment on column "USER_GROUP"."REMARK" is '备注';
comment on column "USER_GROUP"."CREATED_BY" is '创建人';
comment on column "USER_GROUP"."CREATED_TIME" is '创建时间';
comment on column "USER_GROUP"."UPDATED_BY" is '更新人';
comment on column "USER_GROUP"."UPDATED_TIME" is '更新时间';
create index "ix_USER_GROUP_USER_NO" on "USER_GROUP" ("USER_NO");
create index "ix_USER_GROUP_GROUP_NO" on "USER_GROUP" ("GROUP_NO");


-- 用户登录信息表
create table "USER_LOGIN_INFO"
(
    "ID"           serial      primary key,
    "USER_NO"      varchar(32) not null,
    "LOGIN_NAME"   varchar(64) not null,
    "LOGIN_TYPE"   varchar(32) not null,
    "VERSION"      integer     not null,
    "DELETED"      integer     not null,
    "REMARK"       varchar(64),
    "CREATED_BY"   varchar(64),
    "CREATED_TIME" timestamp,
    "UPDATED_BY"   varchar(64),
    "UPDATED_TIME" timestamp
);
comment on column "USER_LOGIN_INFO"."ID" is '主键';
comment on column "USER_LOGIN_INFO"."USER_NO" is '用户编号';
comment on column "USER_LOGIN_INFO"."LOGIN_NAME" is '登录账号';
comment on column "USER_LOGIN_INFO"."LOGIN_TYPE" is '登陆类型（MOBILE:手机号, EMAIL:邮箱, ACCOUNT:账号）';
comment on column "USER_LOGIN_INFO"."VERSION" is '版本号';
comment on column "USER_LOGIN_INFO"."DELETED" is '删除标识';
comment on column "USER_LOGIN_INFO"."REMARK" is '备注';
comment on column "USER_LOGIN_INFO"."CREATED_BY" is '创建人';
comment on column "USER_LOGIN_INFO"."CREATED_TIME" is '创建时间';
comment on column "USER_LOGIN_INFO"."UPDATED_BY" is '更新人';
comment on column "USER_LOGIN_INFO"."UPDATED_TIME" is '更新时间';
create index "ix_USER_LOGIN_INFO_LOGIN_NAME" on "USER_LOGIN_INFO" ("LOGIN_NAME");
create index "ix_USER_LOGIN_INFO_USER_NO" on "USER_LOGIN_INFO" ("USER_NO");


-- 用户登录日志表
create table "USER_LOGIN_LOG"
(
    "ID"           serial      primary key,
    "USER_NO"      varchar(32) not null,
    "LOGIN_NAME"   varchar(64) not null,
    "LOGIN_TYPE"   varchar(32),
    "IP"           varchar(256),
    "VERSION"      integer     not null,
    "DELETED"      integer     not null,
    "REMARK"       varchar(64),
    "CREATED_BY"   varchar(64),
    "CREATED_TIME" timestamp,
    "UPDATED_BY"   varchar(64),
    "UPDATED_TIME" timestamp
);
comment on column "USER_LOGIN_LOG"."ID" is '主键';
comment on column "USER_LOGIN_LOG"."USER_NO" is '用户编号';
comment on column "USER_LOGIN_LOG"."LOGIN_NAME" is '登录账号';
comment on column "USER_LOGIN_LOG"."LOGIN_TYPE" is '登陆类型（MOBILE:手机号, EMAIL:邮箱, ACCOUNT:账号）';
comment on column "USER_LOGIN_LOG"."IP" is 'IP地址';
comment on column "USER_LOGIN_LOG"."VERSION" is '版本号';
comment on column "USER_LOGIN_LOG"."DELETED" is '删除标识';
comment on column "USER_LOGIN_LOG"."REMARK" is '备注';
comment on column "USER_LOGIN_LOG"."CREATED_BY" is '创建人';
comment on column "USER_LOGIN_LOG"."CREATED_TIME" is '创建时间';
comment on column "USER_LOGIN_LOG"."UPDATED_BY" is '更新人';
comment on column "USER_LOGIN_LOG"."UPDATED_TIME" is '更新时间';
create index "ix_USER_LOGIN_LOG_USER_NO" on "USER_LOGIN_LOG" ("USER_NO");


-- 用户密码表
create table "USER_PASSWORD"
(
    "ID"                serial       primary key,
    "USER_NO"           varchar(32)  not null,
    "PASSWORD"          varchar(256) not null,
    "PASSWORD_TYPE"     varchar(16)  not null,
    "LAST_SUCCESS_TIME" timestamp,
    "LAST_ERROR_TIME"   timestamp,
    "ERROR_TIMES"       integer,
    "UNLOCK_TIME"       timestamp,
    "CREATE_TYPE"       varchar(16)  not null,
    "VERSION"           integer      not null,
    "DELETED"           integer      not null,
    "REMARK"            varchar(64),
    "CREATED_BY"        varchar(64),
    "CREATED_TIME"      timestamp,
    "UPDATED_BY"        varchar(64),
    "UPDATED_TIME"      timestamp
);
comment on column "USER_PASSWORD"."ID" is '主键';
comment on column "USER_PASSWORD"."USER_NO" is '用户编号';
comment on column "USER_PASSWORD"."PASSWORD" is '密码';
comment on column "USER_PASSWORD"."PASSWORD_TYPE" is '密码类型（LOGIN:登录密码）';
comment on column "USER_PASSWORD"."LAST_SUCCESS_TIME" is '最后一次密码校验成功时间';
comment on column "USER_PASSWORD"."LAST_ERROR_TIME" is '最后一次密码校验错误时间';
comment on column "USER_PASSWORD"."ERROR_TIMES" is '密码错误次数';
comment on column "USER_PASSWORD"."UNLOCK_TIME" is '解锁时间';
comment on column "USER_PASSWORD"."CREATE_TYPE" is '密码创建类型（CUSTOM:用户自定义, SYSTEM:系统生成）';
comment on column "USER_PASSWORD"."VERSION" is '版本号';
comment on column "USER_PASSWORD"."DELETED" is '删除标识';
comment on column "USER_PASSWORD"."REMARK" is '备注';
comment on column "USER_PASSWORD"."CREATED_BY" is '创建人';
comment on column "USER_PASSWORD"."CREATED_TIME" is '创建时间';
comment on column "USER_PASSWORD"."UPDATED_BY" is '更新人';
comment on column "USER_PASSWORD"."UPDATED_TIME" is '更新时间';
create index "ix_USER_PASSWORD_USER_NO" on "USER_PASSWORD" ("USER_NO");


-- 用户密钥表
create table "USER_SECRET_KEY"
(
    "ID"           serial       primary key,
    "INDEX"        varchar(128) not null,
    "DATA"         text         not null,
    "VERSION"      integer      not null,
    "DELETED"      integer      not null,
    "REMARK"       varchar(64),
    "CREATED_BY"   varchar(64),
    "CREATED_TIME" timestamp,
    "UPDATED_BY"   varchar(64),
    "UPDATED_TIME" timestamp
);
comment on column "USER_SECRET_KEY"."ID" is '主键';
comment on column "USER_SECRET_KEY"."INDEX" is '索引编号';
comment on column "USER_SECRET_KEY"."DATA" is '密钥';
comment on column "USER_SECRET_KEY"."VERSION" is '版本号';
comment on column "USER_SECRET_KEY"."DELETED" is '删除标识';
comment on column "USER_SECRET_KEY"."REMARK" is '备注';
comment on column "USER_SECRET_KEY"."CREATED_BY" is '创建人';
comment on column "USER_SECRET_KEY"."CREATED_TIME" is '创建时间';
comment on column "USER_SECRET_KEY"."UPDATED_BY" is '更新人';
comment on column "USER_SECRET_KEY"."UPDATED_TIME" is '更新时间';
create index "ix_USER_SECRET_KEY_INDEX" on "USER_SECRET_KEY" ("INDEX");


-- 用户设置表
create table "USER_SETTINGS"
(
    "ID"           serial      primary key,
    "USER_NO"      varchar(32) not null,
    "DATA"         jsonb,
    "VERSION"      integer     not null,
    "DELETED"      integer     not null,
    "REMARK"       varchar(64),
    "CREATED_BY"   varchar(64),
    "CREATED_TIME" timestamp,
    "UPDATED_BY"   varchar(64),
    "UPDATED_TIME" timestamp
);
comment on column "USER_SETTINGS"."ID" is '主键';
comment on column "USER_SETTINGS"."USER_NO" is '用户编号';
comment on column "USER_SETTINGS"."DATA" is '用户设置';
comment on column "USER_SETTINGS"."VERSION" is '版本号';
comment on column "USER_SETTINGS"."DELETED" is '删除标识';
comment on column "USER_SETTINGS"."REMARK" is '备注';
comment on column "USER_SETTINGS"."CREATED_BY" is '创建人';
comment on column "USER_SETTINGS"."CREATED_TIME" is '创建时间';
comment on column "USER_SETTINGS"."UPDATED_BY" is '更新人';
comment on column "USER_SETTINGS"."UPDATED_TIME" is '更新时间';
create unique index "ix_USER_SETTINGS_USER_NO" on "USER_SETTINGS" ("USER_NO");


-- 用户角色表
create table "USER_ROLE"
(
    "ID"           serial      primary key,
    "USER_NO"      varchar(32) not null,
    "ROLE_NO"      varchar(32) not null,
    "VERSION"      integer     not null,
    "DELETED"      integer     not null,
    "REMARK"       varchar(64),
    "CREATED_BY"   varchar(64),
    "CREATED_TIME" timestamp,
    "UPDATED_BY"   varchar(64),
    "UPDATED_TIME" timestamp
);
comment on column "USER_ROLE"."ID" is '主键';
comment on column "USER_ROLE"."USER_NO" is '用户编号';
comment on column "USER_ROLE"."ROLE_NO" is '角色编号';
comment on column "USER_ROLE"."VERSION" is '版本号';
comment on column "USER_ROLE"."DELETED" is '删除标识';
comment on column "USER_ROLE"."REMARK" is '备注';
comment on column "USER_ROLE"."CREATED_BY" is '创建人';
comment on column "USER_ROLE"."CREATED_TIME" is '创建时间';
comment on column "USER_ROLE"."UPDATED_BY" is '更新人';
comment on column "USER_ROLE"."UPDATED_TIME" is '更新时间';
create index "ix_USER_ROLE_USER_NO" on "USER_ROLE" ("USER_NO");
create index "ix_USER_ROLE_ROLE_NO" on "USER_ROLE" ("ROLE_NO");


-- 分组表
create table "GROUP"
(
    "ID"           serial       primary key,
    "GROUP_NO"     varchar(32)  not null,
    "GROUP_NAME"   varchar(128) not null,
    "GROUP_DESC"   varchar(128) not null,
    "STATE"        varchar(16)  not null,
    "VERSION"      integer      not null,
    "DELETED"      integer      not null,
    "REMARK"       varchar(64),
    "CREATED_BY"   varchar(64),
    "CREATED_TIME" timestamp,
    "UPDATED_BY"   varchar(64),
    "UPDATED_TIME" timestamp
);
comment on column "GROUP"."ID" is '主键';
comment on column "GROUP"."GROUP_NO" is '分组编号';
comment on column "GROUP"."GROUP_NAME" is '分组名称';
comment on column "GROUP"."GROUP_DESC" is '分组描述';
comment on column "GROUP"."STATE" is '分组状态（ENABLE:启用, DISABLE:禁用）';
comment on column "GROUP"."VERSION" is '版本号';
comment on column "GROUP"."DELETED" is '删除标识';
comment on column "GROUP"."REMARK" is '备注';
comment on column "GROUP"."CREATED_BY" is '创建人';
comment on column "GROUP"."CREATED_TIME" is '创建时间';
comment on column "GROUP"."UPDATED_BY" is '更新人';
comment on column "GROUP"."UPDATED_TIME" is '更新时间';
create unique index "ix_GROUP_GROUP_NO" on "GROUP" ("GROUP_NO");


-- 分组权限表
create table "GROUP_ROLE"
(
    "ID"           serial      primary key,
    "VERSION"      integer     not null,
    "DELETED"      integer     not null,
    "REMARK"       varchar(64),
    "CREATED_BY"   varchar(64),
    "CREATED_TIME" timestamp,
    "UPDATED_BY"   varchar(64),
    "UPDATED_TIME" timestamp,
    "GROUP_NO"     varchar(32) not null,
    "ROLE_NO"      varchar(32) not null
);
comment on column "GROUP_ROLE"."ID" is '主键';
comment on column "GROUP_ROLE"."GROUP_NO" is '分组编号';
comment on column "GROUP_ROLE"."ROLE_NO" is '角色编号';
comment on column "GROUP_ROLE"."VERSION" is '版本号';
comment on column "GROUP_ROLE"."DELETED" is '删除标识';
comment on column "GROUP_ROLE"."REMARK" is '备注';
comment on column "GROUP_ROLE"."CREATED_BY" is '创建人';
comment on column "GROUP_ROLE"."CREATED_TIME" is '创建时间';
comment on column "GROUP_ROLE"."UPDATED_BY" is '更新人';
comment on column "GROUP_ROLE"."UPDATED_TIME" is '更新时间';
create index "ix_GROUP_ROLE_GROUP_NO" on "GROUP_ROLE" ("GROUP_NO");
create index "ix_GROUP_ROLE_ROLE_NO" on "GROUP_ROLE" ("ROLE_NO");


-- 角色表
create table "ROLE"
(
    "ID"           serial       primary key,
    "ROLE_NO"      varchar(32)  not null,
    "ROLE_NAME"    varchar(128) not null,
    "ROLE_CODE"    varchar(64)  not null,
    "ROLE_RANK"    integer      not null,
    "ROLE_DESC"    varchar(256),
    "ROLE_TYPE"    varchar(64),
    "STATE"        varchar(16)  not null,
    "VERSION"      integer      not null,
    "DELETED"      integer      not null,
    "REMARK"       varchar(64),
    "CREATED_BY"   varchar(64),
    "CREATED_TIME" timestamp,
    "UPDATED_BY"   varchar(64),
    "UPDATED_TIME" timestamp
);
comment on column "ROLE"."ID" is '主键';
comment on column "ROLE"."ROLE_NO" is '角色编号';
comment on column "ROLE"."ROLE_NAME" is '角色名称';
comment on column "ROLE"."ROLE_CODE" is '角色代码';
comment on column "ROLE"."ROLE_RANK" is '角色等级';
comment on column "ROLE"."ROLE_DESC" is '角色描述';
comment on column "ROLE"."ROLE_TYPE" is '角色类型（SYSTEM:系统内置, CUSTOM:自定义）';
comment on column "ROLE"."STATE" is '角色状态（ENABLE:启用, DISABLE:禁用）';
comment on column "ROLE"."VERSION" is '版本号';
comment on column "ROLE"."DELETED" is '删除标识';
comment on column "ROLE"."REMARK" is '备注';
comment on column "ROLE"."CREATED_BY" is '创建人';
comment on column "ROLE"."CREATED_TIME" is '创建时间';
comment on column "ROLE"."UPDATED_BY" is '更新人';
comment on column "ROLE"."UPDATED_TIME" is '更新时间';
create unique index "ix_ROLE_ROLE_NO" on "ROLE" ("ROLE_NO");


-- 角色权限表
create table "ROLE_PERMISSION"
(
    "ID"            serial      primary key,
    "ROLE_NO"       varchar(32) not null,
    "PERMISSION_NO" varchar(32) not null,
    "VERSION"       integer     not null,
    "DELETED"       integer     not null,
    "REMARK"        varchar(64),
    "CREATED_BY"    varchar(64),
    "CREATED_TIME"  timestamp,
    "UPDATED_BY"    varchar(64),
    "UPDATED_TIME"  timestamp
);
comment on column "ROLE_PERMISSION"."ID" is '主键';
comment on column "ROLE_PERMISSION"."ROLE_NO" is '角色编号';
comment on column "ROLE_PERMISSION"."PERMISSION_NO" is '权限编号';
comment on column "ROLE_PERMISSION"."VERSION" is '版本号';
comment on column "ROLE_PERMISSION"."DELETED" is '删除标识';
comment on column "ROLE_PERMISSION"."REMARK" is '备注';
comment on column "ROLE_PERMISSION"."CREATED_BY" is '创建人';
comment on column "ROLE_PERMISSION"."CREATED_TIME" is '创建时间';
comment on column "ROLE_PERMISSION"."UPDATED_BY" is '更新人';
comment on column "ROLE_PERMISSION"."UPDATED_TIME" is '更新时间';
create index "ix_ROLE_PERMISSION_ROLE_NO" on "ROLE_PERMISSION" ("ROLE_NO");
create index "ix_ROLE_PERMISSION_PERMISSION_NO" on "ROLE_PERMISSION" ("PERMISSION_NO");


------------------------------⬆️ usercenter ⬆️------------------------------


------------------------------⬇️ system ⬇️------------------------------
-- 工作空间表
create table "WORKSPACE"
(
    "ID"              serial       primary key,
    "WORKSPACE_NO"    varchar(32)  not null,
    "WORKSPACE_NAME"  varchar(128) not null,
    "WORKSPACE_SCOPE" varchar(128) not null,
    "WORKSPACE_DESC"  varchar(256),
    "VERSION"         integer      not null,
    "DELETED"         integer      not null,
    "REMARK"          varchar(64),
    "CREATED_BY"      varchar(64),
    "CREATED_TIME"    timestamp,
    "UPDATED_BY"      varchar(64),
    "UPDATED_TIME"    timestamp
);
comment on column "WORKSPACE"."ID" is '主键';
comment on column "WORKSPACE"."WORKSPACE_NO" is '空间编号';
comment on column "WORKSPACE"."WORKSPACE_NAME" is '空间名称';
comment on column "WORKSPACE"."WORKSPACE_SCOPE" is '空间作用域';
comment on column "WORKSPACE"."WORKSPACE_DESC" is '空间描述';
comment on column "WORKSPACE"."VERSION" is '版本号';
comment on column "WORKSPACE"."DELETED" is '删除标识';
comment on column "WORKSPACE"."REMARK" is '备注';
comment on column "WORKSPACE"."CREATED_BY" is '创建人';
comment on column "WORKSPACE"."CREATED_TIME" is '创建时间';
comment on column "WORKSPACE"."UPDATED_BY" is '更新人';
comment on column "WORKSPACE"."UPDATED_TIME" is '更新时间';
create unique index "ix_WORKSPACE_WORKSPACE_NO" on "WORKSPACE" ("WORKSPACE_NO");


-- 空间成员表
create table "WORKSPACE_USER"
(
    "ID"           serial      primary key,
    "WORKSPACE_NO" varchar(32) not null,
    "USER_NO"      varchar(32) not null,
    "VERSION"      integer     not null,
    "DELETED"      integer     not null,
    "REMARK"       varchar(64),
    "CREATED_BY"   varchar(64),
    "CREATED_TIME" timestamp,
    "UPDATED_BY"   varchar(64),
    "UPDATED_TIME" timestamp
);
comment on column "WORKSPACE_USER"."ID" is '主键';
comment on column "WORKSPACE_USER"."WORKSPACE_NO" is '空间编号';
comment on column "WORKSPACE_USER"."USER_NO" is '用户编号';
comment on column "WORKSPACE_USER"."VERSION" is '版本号';
comment on column "WORKSPACE_USER"."DELETED" is '删除标识';
comment on column "WORKSPACE_USER"."REMARK" is '备注';
comment on column "WORKSPACE_USER"."CREATED_BY" is '创建人';
comment on column "WORKSPACE_USER"."CREATED_TIME" is '创建时间';
comment on column "WORKSPACE_USER"."UPDATED_BY" is '更新人';
comment on column "WORKSPACE_USER"."UPDATED_TIME" is '更新时间';
create index "ix_WORKSPACE_USER_USER_NO" on "WORKSPACE_USER" ("USER_NO");
create index "ix_WORKSPACE_USER_WORKSPACE_NO" on "WORKSPACE_USER" ("WORKSPACE_NO");


------------------------------⬆️ system ⬆️------------------------------
