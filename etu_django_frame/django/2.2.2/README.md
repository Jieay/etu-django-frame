#2020/5/1
1. django 2.2.2开发框架目录规划。

2. 各目录说明：  
2.1. frame_server目录，它是project级别。  
2.2. app目录，应用程序开发目录，目前规划是所有的api入口。  
2.3. data目录，存放django后台管理所需要的静态文件。  
2.4. docs目录，存放部署文档。  
2.5. requirements目录，用来存放pip包清单。   
2.6. utils目录，python包类型，用于存放公共组件。  

3. app目录说明：  
3.1. 将admin.py, models.py, tasks.py和views.py全部改为包类型。 

4. 接口的版本规划，GET方式请求，分别为：
    * api/v1/hello
    
5. 配置文件划分，开发、测试和生产环境，主要区别是数据库的配置不同，以后不同的配置再进行添加。默认为开发环境，即使用config_dev配置文件。如果要使用别的配置文件请设置环境变量 SERVER_CFG，可配置值分别为dev、 test、staging和production。