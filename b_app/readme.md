
## 部署
* 主要是实现功能，数据库采用sqlite3,不依赖其它数据库服务
* 对sqlite做了层封装，支持multiprocess.从而兼容其它接口，
如uwsgi, gunicorn等可分离出多个process的接口。

## linux下安装python
* 请按照相关文档安装python,若linux下sqlite及其dev库缺失，
编译出的python是无sqlite模块
* 同理 _atexit

## 吞吐量
* 只是简单demo, 没做缓存，也没有采用其它高吞吐的数据库，
不过可以满足一般需求
* 支持吞吐量相对较高的版本:[simple-blog-gin](https://github.com/QHtzs/simple-blog-gin.git)

## 采用的非前后端分离模式
* 前端不大会，到处也没有扣到多少好看的前端，随便撸了几页
* 页面太丑请见谅
