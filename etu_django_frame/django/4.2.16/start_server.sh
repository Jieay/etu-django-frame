#!/bin/bash
#export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python
#export PIP_VIRTUALENV_BASE=$WORKON_HOME
#export PIP_RESPECT_VIRTUALENV=true
#source `which virtualenvwrapper.sh`
#
# working_dir="/data/test/xxx_xxx_xxx"
# cd $working_dir
# workon xxx_xxx_xxx

uwsgi --ini uwsgi_config.ini