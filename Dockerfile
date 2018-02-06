FROM python:3

ARG APP_NAME

WORKDIR /usr/src/app

# Install common package
COPY common ./common
RUN pip install ./common

# Install application
COPY $APP_NAME $APP_NAME

WORKDIR /usr/src/app/$APP_NAME
RUN pip install .

EXPOSE 8080
