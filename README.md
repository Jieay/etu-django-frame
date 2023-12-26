# 概括
    etu 系列（easy to use）
    让技术更容易使用！
    EDF脚手架工具(Etu Django Frame)是在开源Django框架的基础上封装而成，以更快捷简便的命令方式，快速创建项目工程，以方便开发使用。
    

## 说明
    本包名字为 etu-django-frame , 它主要是EDF脚手架工具的封装。其中支持的Django框架版本：2.2.2、3.2.13、4.2.2


### 打包方法
    1. 将要打包的代码文件，统一放在一个目录中，目录名就是pip包的名字；
    2. 在目录外创建一个setup.py文件，并配置好；
    3. 执行 python setup.py sdist命令，完成打包；
    4. 完成打包后，便可通过 pip install 命令进行安装。

### 安装方法
    通过pip命令进行安装：pip install etu-django-frame
   

### 参数说明
```shell
usage: edf-admin label project_name
labels:
    3.2.13
    4.2.2
```


### 使用方法
```shell
cd ~
edf-admin 4.2.2 demo_01
```


### 错误反馈