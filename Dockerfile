FROM python:3

ARG APP_NAME

WORKDIR /usr/src/app

COPY $APP_NAME $APP_NAME
COPY common ./common

EXPOSE 8080

WORKDIR /usr/src/app/$APP_NAME
RUN pip install -r requirements.txt
