#2022/1/20
## Django 3.2.13 框架开发说明

### 1. 目录说明：
1.1. frame_server目录，项目主目录，框架相关配置。   
1.2. app目录，应用目录，业务相关的应用程序开发模块，models、views、urls等，并且将admin.py, models.py, tasks.py和views.py全部改为包类型。    
1.3. data目录，资源目录，存放django后台管理所需要的静态文件以及其他临时文件。    
1.4. docs目录，文档目录，存放部署、发布相关文档。    
1.5. requirements目录，库依赖目录，管理pip库依赖文件以及依赖包。    
1.6. utils目录，工具目录，用于存放公共组件以及自定义封装API      

### 2. 接口规划说明   
2.1 接口采用版本方式，GET方式请求，示例：   
```shell
    * /api/v1/hello/
```

### 3. 配置说明   
3.1 配置文件划分，开发、测试、UAT和生产环境，主要区别是数据库的配置不同，以后不同的配置再进行添加。默认为开发环境，即使用config_dev配置文件。如果要使用别的配置文件请设置环境变量 SERVER_CFG，可配置值分别为dev、 test、staging和production。

### 4. 容器说明   
4.1 启动容器   
```shell
# 启动主服务
docker run -d --name demo-pdf -p 11025:11025 image:tag
# 启动 celery beat
docker run -d --name demo-beat -e START_SERVICE=beat image:tag
# 启动 celery worker
docker run -d --name demo-worker -e START_SERVICE=worker image:tag 
```
