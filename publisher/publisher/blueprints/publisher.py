from flask import Blueprint, request, session, g, redirect, url_for, abort, \
     render_template, flash, current_app
from ngcd_common import events_pb2
from google.protobuf.timestamp_pb2 import Timestamp
import pika
import datetime

# create our blueprint :)
bp = Blueprint('publisher', __name__)

def timestamp_from_dt(dt):
    ts = Timestamp()
    ts.FromDatetime(dt)

    return ts

def connect_rabbitmq():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=current_app.config['RABBITMQ_HOST']))
    connection.channel().exchange_declare(exchange='external',
                                          exchange_type='topic')
    return connection.channel()

def get_rabbitmq():
    if not hasattr(g, 'rabbitmq'):
        g.rabbitmq = connect_rabbitmq()
    return g.rabbitmq

@bp.route("/pipeline_started/<uuid>")
def pipeline_started(uuid=None):
    rabbitmq = get_rabbitmq()
    ts = timestamp_from_dt(datetime.datetime.now())
    event = events_pb2.PipelineStarted(uuid=uuid,
                                       timestamp=ts)
    rabbitmq.basic_publish(exchange='external',
                           routing_key='pipeline.started',
                           body=event.SerializeToString(),
                           properties=pika.BasicProperties(
                              delivery_mode = 2, # make message persistent
                           ))
    return " [x] Sent PipelineStarted"

@bp.route("/pipeline_finished/<uuid>")
def pipeline_finished(uuid=None):
    rabbitmq = get_rabbitmq()
    ts = timestamp_from_dt(datetime.datetime.now())
    event = events_pb2.PipelineFinished(uuid=uuid,
                                       timestamp=ts,
                                       result=events_pb2.SUCCESS)
    rabbitmq.basic_publish(exchange='external',
                           routing_key='pipeline.finished',
                           body=event.SerializeToString(),
                           properties=pika.BasicProperties(
                              delivery_mode = 2, # make message persistent
                           ))
    return " [x] Sent PipelineFinished"

@bp.route("/pipeline_stage_started/<uuid>/<pipeline_uuid>")
def pipeline_stage_started(uuid=None, pipeline_uuid=None):
    rabbitmq = get_rabbitmq()
    ts = timestamp_from_dt(datetime.datetime.now())
    event = events_pb2.PipelineStageStarted(uuid=uuid,
                                            pipeline_uuid=pipeline_uuid,
                                            timestamp=ts)
    rabbitmq.basic_publish(exchange='external',
                           routing_key='pipeline.stage.started',
                           body=event.SerializeToString(),
                           properties=pika.BasicProperties(
                              delivery_mode = 2, # make message persistent
                           ))
    return " [x] Sent PipelineStarted"

@bp.route("/pipeline_stage_finished/<uuid>/<pipeline_uuid>")
def pipeline_stage_finished(uuid=None, pipeline_uuid=None):
    rabbitmq = get_rabbitmq()
    ts = timestamp_from_dt(datetime.datetime.now())
    event = events_pb2.PipelineStageFinished(uuid=uuid,
                                             pipeline_uuid=pipeline_uuid,
                                             timestamp=ts,
                                             result=events_pb2.ABORTED)
    rabbitmq.basic_publish(exchange='external',
                           routing_key='pipeline.stage.finished',
                           body=event.SerializeToString(),
                           properties=pika.BasicProperties(
                              delivery_mode = 2, # make message persistent
                           ))
    return " [x] Sent PipelineFinished"

@bp.route("/push/<reponame>/<sha>", methods=['POST'])
def codepushed(reponame=None, sha=None):
    """ Example payload:
    {
        "new_head_sha": "23456",
        "previous_head_sha": "00000",
        "user": {
            "id": "1",
            "username": "svante",
            "email": "svante@paldan.se"
        },
        "commits": [
            {
                "sha": "12345",
                "message": "test commit!"
            },
            {
                "sha": "23456",
                "message": "test commit number 2!"
            }
        ]
    }
    """
    payload = request.get_json(force=True)
    user = events_pb2.ScmUser(id=payload['user']['id'],
                              username=payload['user']['username'],
                              email=payload['user']['email'])

    commits = []
    if 'commits' in payload:
        for commit in payload['commits']:
            commits.append(events_pb2.ScmCommit(sha=commit['sha'],
                                                message=commit['message'],
                                                author=user,
                                                timestamp=timestamp_from_dt(datetime.datetime.now())))
    ts = timestamp_from_dt(datetime.datetime.now())

    rabbitmq = get_rabbitmq()
    ts = timestamp_from_dt(datetime.datetime.now())
    event = events_pb2.CodePushed(repository_name=reponame,
                                  new_head_sha=payload['new_head_sha'],
                                  previous_head_sha=payload['previous_head_sha'],
                                  pusher=user,
                                  commits=commits,
                                  timestamp=ts)

    rabbitmq.basic_publish(exchange='external',
                           routing_key='scm.repo.push',
                           body=event.SerializeToString(),
                           properties=pika.BasicProperties(
                              delivery_mode = 2, # make message persistent
                           ))
    return " [x] Sent CodePushed"
