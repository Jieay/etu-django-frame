FROM jieay/python-comm:3.6
ENV PYTHONUNBUFFERED 1

WORKDIR /code

ADD . .

RUN pip install --no-cache-dir --trusted-host mirrors.aliyun.com -i \
    https://mirrors.aliyun.com/pypi/simple/ -r requirements/requirement.txt \
    && chmod +x /code/*.sh

ENV START_SERVICE master

EXPOSE 11025

CMD ["/code/docker_start.sh"]

