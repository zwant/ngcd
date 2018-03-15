FROM python:3

ARG APP_NAME

WORKDIR /usr/src/app

# Install common package
COPY common ./common
RUN pip install -r ./common/requirements-prod.txt
RUN pip install -e ./common

# Install application
COPY $APP_NAME $APP_NAME

WORKDIR /usr/src/app/$APP_NAME
RUN pip install -r requirements-prod.txt
RUN pip install -e .

EXPOSE 8080
