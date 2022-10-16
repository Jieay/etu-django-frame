# -*- coding: utf-8 -*-
# @Time    : 2022/9/17 15:47
# @Author  : Jieay
# @File    : main.py
import os
import shutil
import sys
import uuid
from pathlib import Path
from . import __version__

BASE_DIR = Path(__file__).resolve().parent


class ManagementUtility:
    """
    Encapsulate the logic of the pdf-admin utilities.
    """
    VERSION_LIST = ['3.2.13', '2.2.2']

    def __init__(self, argv=None):
        self.argv = argv or sys.argv[:]
        self.prog_name = os.path.basename(self.argv[0])
        self.version_list = self.VERSION_LIST
        self.cwd_dir = os.getcwd()
        self.data_root_dir = os.path.join(BASE_DIR, 'data')
        self.frame_root_dir = os.path.join(BASE_DIR, 'django')
        self.frame_name = 'frame_server'

    def main_help_text(self):
        """Return the script's main help text, as a string."""
        label_name = '\n'.join(['    {}'.format(x) for x in self.version_list])
        usage = [
            "",
            "usage: edf-admin label project_name",
            "labels: ",
            label_name,
        ]
        return '\n'.join(usage)

    def replace_content_read(self, file_name):
        """
        替换内容，读文件内容
        :param file_name: 文件路径
        :return: 文件内容
        """
        with open(file_name, 'r') as f:
            new_content = f.read()
        return new_content

    def replace_content_write(self, file_name, content):
        """
        替换内容，写文件
        :param file_name: 文件路径
        :param content: 文件内容
        :return: 文件路径
        """
        with open(file_name, 'w') as f:
            f.write(content)
        return file_name

    def change_rename(self, old_data, new_data):
        """
        文件或者目录重命名
        :param old_data: 旧未文件或者目录
        :param new_data: 新文件或者目录
        :return: `bool`
        """
        try:
            os.rename(old_data, new_data)
            return True
        except FileNotFoundError:
            return False

    def check_file_exists(self, file_path):
        """
        检查目标是否是文件
        :param file_path: 文件路径
        :return: `bool`
        """
        if os.path.isfile(file_path):
            return True
        return False

    def change_file_to_project_name(self, file_name, project_name):
        """
        更改脚手架项目名称
        :param file_name: 文件路径
        :param project_name: 项目名
        """
        name = os.path.basename(file_name)
        file_path = os.path.dirname(file_name)

        # 将 gitignore 文件重命名
        if name == 'gitignore':
            self.change_rename(file_name, os.path.join(file_path, '.gitignore'))
        else:
            old_content = self.replace_content_read(file_name)
            new_name = uuid.uuid4().hex
            new_file_name = os.path.join(file_path, new_name)
            new_content = old_content.replace(self.frame_name, project_name)
            self.replace_content_write(new_file_name, new_content)
            if os.path.exists(file_name):
                os.remove(file_name)
            # 将修改内容文件重命名原来的文件
            self.change_rename(new_file_name, file_name)

    def change_frame_project_name(self, project_name, cf_path_list):
        """
        修改脚手架项目名称
        :param project_name: 项目名
        :param cf_path_list: 修改文件路径列表
        """
        for cf_file in cf_path_list:
            self.change_file_to_project_name(file_name=cf_file, project_name=project_name)

    def _check_file_path_list(self, project_name, tmp_data, change_file_list):
        """
        检查文件路径列表
        :param project_name: 项目名
        :param tmp_data: 临时目录路径
        :param change_file_list: 修改文件列表
        :return: `list` ['/xxx/xxx/xxx.py', '/aaa/aaa/aaa.py']
        """
        cf_path_list = []
        for name in change_file_list:
            if isinstance(name, list):
                for sub_name in name:
                    old_project_path = os.path.join(tmp_data, self.frame_name)
                    project_path = os.path.join(tmp_data, project_name)
                    if not os.path.exists(project_path) and os.path.exists(old_project_path):
                        self.change_rename(old_project_path, project_path)
                    file_path = os.path.join(project_path, sub_name)
                    if self.check_file_exists(file_path):
                        cf_path_list.append(file_path)
            else:
                if '/' in name:
                    name_list = name.split('/')
                    file_path = os.path.join(tmp_data, *name_list)
                else:
                    file_path = os.path.join(tmp_data, name)
                if self.check_file_exists(file_path):
                    cf_path_list.append(file_path)
        return cf_path_list

    def change_222(self, project_name, tmp_data):
        """修改Django 2.2.2 版本脚手架文件"""
        change_file_list = [
            'config_dev', 'config_dist', 'manage.py', 'README.md', 'gitignore',
            [
                'celery.py', 'settings.py', 'wsgi.py', 'urls.py'
            ],
            'app/tasks/demo_test.py',
        ]
        cf_path_list = self._check_file_path_list(
            project_name=project_name, tmp_data=tmp_data, change_file_list=change_file_list
        )
        self.change_frame_project_name(project_name=project_name, cf_path_list=cf_path_list)

    def change_3213(self, project_name, tmp_data):
        """修改Django 3.2.13 版本脚手架文件"""
        change_file_list = [
            'config_dev', 'config_dist', 'manage.py', 'README.md', 'gitignore',
            [
                'celery.py', 'settings.py', 'wsgi.py', 'urls.py', 'asgi.py'
            ],
            'app/tasks/demo_test.py', 'supervisord.conf', 'uwsgi_config.ini',
            'celery_beat.sh', 'celery_worker.sh',
        ]
        cf_path_list = self._check_file_path_list(
            project_name=project_name, tmp_data=tmp_data, change_file_list=change_file_list
        )
        self.change_frame_project_name(project_name=project_name, cf_path_list=cf_path_list)

    def change_frame_file(self, label, project_name, tmp_data):
        """修改不同Django版本脚手架文件"""
        if label == '2.2.2':
            self.change_222(project_name, tmp_data)

        elif label == '3.2.13':
            self.change_3213(project_name, tmp_data)

    def create_frame(self, label, project_name):
        """
        创建脚手架项目文件
        :param label: Django版本
        :param project_name: 项目名称
        """
        if not os.path.exists(self.data_root_dir):
            os.makedirs(self.data_root_dir)
        tmp_data_dir = os.path.join(self.data_root_dir, uuid.uuid4().hex)
        frame_source_dir = os.path.join(self.frame_root_dir, label)
        # 创建临时文件
        if not os.path.exists(tmp_data_dir):
            shutil.copytree(frame_source_dir, tmp_data_dir)

        self.change_frame_file(label=label, project_name=project_name, tmp_data=tmp_data_dir)

        # 创建项目目录，生产脚手架稳文件
        create_project_dir = os.path.join(self.cwd_dir, project_name)
        if not os.path.exists(create_project_dir):
            shutil.copytree(tmp_data_dir, create_project_dir)

        # 删除临时文件
        if os.path.exists(tmp_data_dir):
            shutil.rmtree(tmp_data_dir)

        sys.stdout.write('Create finished.' + '\n')

    def execute(self):
        """
        Given the command-line arguments, figure out which subcommand is being
        run, create a parser appropriate to that command, and run it.
        """
        sys.stdout.write('Welcome to PDF tools.' + '\n')
        try:
            subcommand = self.argv[1]
        except IndexError:
            subcommand = 'help'  # Display help if no arguments were given.

        if subcommand in self.version_list:
            sys.stdout.write('Select the django version: {}'.format(subcommand) + '\n')
            try:
                project_name = self.argv[2]
            except IndexError:
                project_name = None

            if project_name:
                if '-' in project_name:
                    sys.stdout.write('The project_name【{}】cannot use the - character.'.format(project_name) + '\n')
                    exit(0)
                sys.stdout.write('Create project name: {}'.format(project_name) + '\n')
                self.create_frame(label=subcommand, project_name=project_name)
            else:
                sys.stdout.write(self.main_help_text() + '\n')

        elif subcommand == 'help':
            sys.stdout.write(self.main_help_text() + '\n')

        # Special-cases: We want 'pdf-admin --version' and
        # 'pdf-admin --help' to work, for backwards compatibility.
        elif subcommand == 'version' or self.argv[1:] == ['--version']:
            sys.stdout.write(__version__ + '\n')

        elif self.argv[1:] in (['--help'], ['-h']):
            sys.stdout.write(self.main_help_text() + '\n')
        else:
            sys.stdout.write(self.main_help_text() + '\n')


def execute_from_command_line(argv=None):
    """Run a ManagementUtility."""
    utility = ManagementUtility(argv)
    utility.execute()
