FROM python:3.6
ENV PYTHONUNBUFFERED 1
ADD requirements /requirements
RUN pip install --no-cache-dir -r requirements/requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
RUN mkdir /code
WORKDIR /code
ADD ./ /code/
RUN chmod +x /code/docker_start.sh
EXPOSE 8000
CMD ["/code/docker_start.sh"]

