FROM python:3.9-slim-bullseye

ENV HTTPS_PROXY http://proxy-server.sovcombank.group:3128
ENV HTTP_PROXY http://proxy-server.sovcombank.group:3128
ENV https_proxy http://proxy-server.sovcombank.group:3128
ENV http_proxy http://proxy-server.sovcombank.group:3128
ENV NO_PROXY "127.0.0.1,localhost,.sovcombank.group,minio,.sovcombank.ru,kubernetes,.default.svc.cluster.local,coroot-clickhouse,coroot-clickhouse.coroot-clickhouse"

WORKDIR /app

RUN apt update -y && apt install ca-certificates curl -y

COPY /app/requirements.txt .

RUN pip3 install -r requirements.txt --no-cache-dir

COPY ./app/ /app/ 

RUN chmod +x /app/manager.py

USER nobody

ENTRYPOINT [ "/app/manager.py" ]
