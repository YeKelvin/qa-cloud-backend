# RESTful API

## 一、协议
使用HTTPs协议

## 二、域名
将API部署在专用域名之下
```
https://api.example.com
```

如果确定API很简单，不会有进一步扩展，可以考虑放在主域名下
```
https://example.org/api/
```

## 三、版本
应该将API的版本号放入URL
```
https://api.example.com/v1/
```

## 四、路径
路径又称"终点"（endpoint），表示API的具体网址。

在RESTful中，每个网址代表一种资源（resource），所以网址中不能有动词，只能有名词，而且所用的名词往往与数据库的表格名对应。

一般来说，数据库中的表都是同种记录的"集合"（collection），所以API中的名词也应该使用复数。
```
https://api.example.com/v1/users
https://api.example.com/v1/menus
```

## 五、HTTP动词
对于资源的具体操作类型，由HTTP动词表示。

#### 常用的HTTP动词有下面五个，对应SQL命令如下
```
GET         SELECT      从服务器取出资源（一项或多项）
POST        CREATE      在服务器新建一个资源
PUT         UPDATE      在服务器更新资源（客户端提供改变后的完整资源）
PATCH       UPDATE      在服务器更新资源（客户端提供改变的属性）
DELETE      DELETE      从服务器删除资源
```

#### 路由路径命名规范
```
GET         /user/list              分页查询用户列表
GET         /user/all               查询所有用户
POST        /user                   新增用户
PUT         /user                   修改用户信息
PATCH       /user/attribute         修改用户的名称
DELETE      /user                   删除用户
```

#### Python路由方法命名规范
```
GET         def user_list()             分页查询用户列表
GET         def user_all()              查询所有用户
POST        def create_user()           新增用户
PUT         def modify_user()           修改用户信息
PATCH       def modify_user_name()      修改用户的名称
DELETE      def delete_user()           删除用户
```
