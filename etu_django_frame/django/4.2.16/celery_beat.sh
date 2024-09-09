#!/bin/bash
# export VIRTUALENVWRAPPER_PYTHON=/bin/python3
# export PIP_VIRTUALENV_BASE=$WORKON_HOME
# export PIP_RESPECT_VIRTUALENV=true
# source `which virtualenvwrapper.sh`

# working_dir="/data/test/xxx_xxx_xxx"
# cd $working_dir
# workon xxx_xxx_xxx
# 禁用断言
export PYTHONOPTIMIZE=1

celery -A frame_server beat -l info