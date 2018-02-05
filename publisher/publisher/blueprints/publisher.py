from flask import Blueprint, request, session, g, redirect, url_for, abort, \
     render_template, flash, current_app
from ngcd_common import events_pb2
from google.protobuf.timestamp_pb2 import Timestamp
import pika
import datetime
from random import randint

# create our blueprint :)
bp = Blueprint('publisher', __name__)

def timestamp_from_json_string(json_string):
    ts = Timestamp()
    ts.FromJsonString(json_string)

    return ts

def connect_rabbitmq():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=current_app.config['RABBITMQ_HOST']))
    connection.channel().exchange_declare(exchange='external',
                                          durable=True,
                                          exchange_type='topic')
    return connection.channel()

def get_rabbitmq():
    if not hasattr(g, 'rabbitmq'):
        g.rabbitmq = connect_rabbitmq()
    return g.rabbitmq

@bp.route("/pipeline_started/<uuid>/", methods=['POST'])
def pipeline_started(uuid=None):
    """ Example payload:
    {
        "timestamp": "2012-04-23T18:25:43.511Z"
    }
    """
    payload = request.get_json(force=True)

    rabbitmq = get_rabbitmq()
    ts = timestamp_from_json_string(payload['timestamp'])
    event = events_pb2.PipelineStarted(uuid=uuid,
                                       timestamp=ts)
    rabbitmq.basic_publish(exchange='external',
                           routing_key='pipeline.started',
                           body=event.SerializeToString(),
                           properties=pika.BasicProperties(
                              delivery_mode = 2, # make message persistent
                           ))
    return " [x] Sent PipelineStarted"

@bp.route("/pipeline_finished/<uuid>/", methods=['POST'])
def pipeline_finished(uuid=None):
    """ Example payload:
    {
        "timestamp": "2012-04-23T18:25:43.511Z",
        "duration_ms": 123456,
        "result": "SUCCESS"
    }

    Result can be one of: [SUCCESS, FAILURE, ABORTED]
    """
    payload = request.get_json(force=True)
    ts = timestamp_from_json_string(payload['timestamp'])
    event = events_pb2.PipelineFinished(uuid=uuid,
                                       timestamp=ts,
                                       result=events_pb2.Result.Value(payload['result']),
                                       duration_ms=payload['duration_ms'])

    rabbitmq = get_rabbitmq()
    rabbitmq.basic_publish(exchange='external',
                           routing_key='pipeline.finished',
                           body=event.SerializeToString(),
                           properties=pika.BasicProperties(
                              delivery_mode = 2, # make message persistent
                           ))
    return " [x] Sent PipelineFinished"

@bp.route("/pipeline_stage_started/<uuid>/", methods=['POST'])
def pipeline_stage_started(uuid=None):
    """ Example payload:
    {
        "timestamp": "2012-04-23T18:25:43.511Z",
        "pipeline_uuid": "svante"
    }

    """
    payload = request.get_json(force=True)
    ts = timestamp_from_json_string(payload['timestamp'])

    event = events_pb2.PipelineStageStarted(uuid=uuid,
                                            pipeline_uuid=payload['pipeline_uuid'],
                                            timestamp=ts)
    rabbitmq = get_rabbitmq()
    rabbitmq.basic_publish(exchange='external',
                           routing_key='pipeline.stage.started',
                           body=event.SerializeToString(),
                           properties=pika.BasicProperties(
                              delivery_mode = 2, # make message persistent
                           ))
    return " [x] Sent PipelineStarted"

@bp.route("/pipeline_stage_finished/<uuid>/", methods=['POST'])
def pipeline_stage_finished(uuid=None):
    """ Example payload:
    {
        "timestamp": "2012-04-23T18:25:43.511Z",
        "pipeline_uuid": "svante",
        "duration_ms": 123456,
        "result": "SUCCESS"
    }

    Result can be one of: [SUCCESS, FAILURE, ABORTED]
    """
    payload = request.get_json(force=True)
    ts = timestamp_from_json_string(payload['timestamp'])

    event = events_pb2.PipelineStageFinished(uuid=uuid,
                                             pipeline_uuid=payload['pipeline_uuid'],
                                             timestamp=ts,
                                             result=events_pb2.Result.Value(payload['result']),
                                             duration_ms=payload['duration_ms'])
    rabbitmq = get_rabbitmq()
    rabbitmq.basic_publish(exchange='external',
                           routing_key='pipeline.stage.finished',
                           body=event.SerializeToString(),
                           properties=pika.BasicProperties(
                              delivery_mode = 2, # make message persistent
                           ))
    return " [x] Sent PipelineFinished"

@bp.route("/push/<reponame>/<sha>/", methods=['POST'])
def codepushed(reponame=None, sha=None):
    """ Example payload:
    {
        "timestamp": "2012-04-23T18:25:43.511Z",
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
                "timestamp": "2012-04-23T18:25:43.511Z",
                "message": "test commit!"
            },
            {
                "sha": "23456",
                "timestamp": "2012-04-23T18:25:43.511Z",
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
                                                timestamp=timestamp_from_json_string(commit['timestamp'])))
    ts = timestamp_from_json_string(payload['timestamp'])

    rabbitmq = get_rabbitmq()
    ts = timestamp_from_json_string(payload['timestamp'])
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
