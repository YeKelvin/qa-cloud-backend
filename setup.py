import pathlib

from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent
with open(f'{HERE}/README.md', 'r', encoding='utf-8') as f:
    README = f.read()

setup(
    name='test-platform-server',
    version='0.1',
    description='',
    long_description=README,
    long_description_content_type='text/markdown',
    url='',
    license='',
    author='Kaiwen.Ye',
    author_email='testmankelvin@163.com',
    packages=find_packages(exclude=('test',)),
    include_package_data=True,
    install_requires=[
        'orjson'
        'grpcio',
        'grpcio-tools',
        'requests',
        'uwsgi; platform_system == "Linux"'
    ],
    extras_require={'test': []},
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ])

"""
一、Option选项说明
|-----------------------|-------------------------------------------------------
|option                 |说明
|-----------------------|-------------------------------------------------------
|name	                |包名称
|version	            |包版本
|author	                |程序的作者
|author_email	        |程序的作者的邮箱地址
|maintainer	            |维护者
|maintainer_email	    |维护者的邮箱地址
|url	                |程序的官网地址
|license	            |程序的授权信息
|description	        |程序的简单描述
|long_description	    |程序的详细描述
|platforms	            |程序适用的软件平台列表
|classifiers	        |程序的所属分类列表
|keywords	            |程序的关键字列表
|packages	            |需要处理的包目录(通常为包含 __init__.py 的文件夹)
|py_modules	            |需要打包的 Python 单文件列表
|download_url	        |程序的下载地址
|cmdclass	            |添加自定义命令
|package_data	        |指定包内需要包含的数据文件
|include_package_data	|自动包含包内所有受版本控制(cvs/svn/git)的数据文件
|exclude_package_data	|当 include_package_data 为 True 时该选项用于排除部分文件
|data_files	            |打包时需要打包的数据文件，如图片，配置文件等
|ext_modules	        |指定扩展模块
|scripts	            |指定可执行脚本,安装时脚本会被安装到系统 PATH 路径下
|package_dir	        |指定哪些目录下的文件被映射到哪个源码包
|requires	            |指定依赖的其他包
|provides	            |指定可以为哪些模块提供依赖
|install_requires	    |安装时需要安装的依赖包
|entry_points	        |动态发现服务和插件，下面详细讲
|setup_requires	        |指定运行 setup.py 文件本身所依赖的包
|dependency_links	    |指定依赖包的下载地址
|extras_require	        |当前包的高级/额外特性需要依赖的分发包
|zip_safe	            |不压缩包，而是以目录的形式安装
|-----------------------|-------------------------------------------------------

二、根据不同操作系统安装不同的依赖
install_requires = [
    'winkerberos; platform_system == "Windows"',
    'pykerberos; platform_system == "Linux"',
]
"""
