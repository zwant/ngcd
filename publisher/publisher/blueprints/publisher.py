from flask import Blueprint, request, session, g, redirect, url_for, abort, \
     render_template, flash, current_app
from ngcd_common import events_pb2, queue_configs
from google.protobuf.timestamp_pb2 import Timestamp
from kombu import Connection
import datetime
from random import randint

# create our blueprint :)
bp = Blueprint('publisher', __name__)


def timestamp_from_json_string(json_string):
    ts = Timestamp()
    ts.FromJsonString(json_string)

    return ts

def connect_rabbitmq():
    connection = Connection(current_app.config['RABBITMQ_CONNECTION_STRING'])
    producer = connection.Producer()

    return producer

def get_rabbitmq():
    if not hasattr(g, 'rabbitmq'):
        g.rabbitmq = connect_rabbitmq()
    return g.rabbitmq

def publish_to_queue(rabbitmq, protobuf_obj, queue):
    rabbitmq.publish(
        protobuf_obj.SerializeToString(),
        retry=True,
        exchange=queue_configs.EXTERNAL_EXCHANGE,
        routing_key=queue.routing_key,
        content_type='application/vnd.google.protobuf',
        content_encoding='binary',
        delivery_mode=2,
        declare=[queue]  # declares exchange, queue and binds.
    )

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

    queue = queue_configs.EXTERNAL_QUEUES['pipeline.started']
    publish_to_queue(rabbitmq, event, queue)
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

    queue = queue_configs.EXTERNAL_QUEUES['pipeline.finished']
    publish_to_queue(rabbitmq, event, queue)
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
    queue = queue_configs.EXTERNAL_QUEUES['pipeline.stage.started']
    publish_to_queue(rabbitmq, event, queue)
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
    queue = queue_configs.EXTERNAL_QUEUES['pipeline.stage.finished']
    publish_to_queue(rabbitmq, event, queue)
    return " [x] Sent PipelineFinished"

@bp.route("/push/", methods=['POST'])
def codepushed():
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

    rabbitmq = get_rabbitmq()
    ts = timestamp_from_json_string(payload['timestamp'])
    event = events_pb2.CodePushed(identifier=events_pb2.RepoIdentifier(
                                    short_name=payload['identifier']['short_name'],
                                    full_name=payload['identifier']['full_name'],
                                    repo_type=payload['identifier']['repo_type']
                                  ),
                                  target_branch=payload['target_branch'],
                                  new_head_sha=payload['new_head_sha'],
                                  previous_head_sha=payload['previous_head_sha'],
                                  pusher=user,
                                  commits=commits,
                                  timestamp=ts)

    queue = queue_configs.EXTERNAL_QUEUES['scm.repo.push']
    publish_to_queue(rabbitmq, event, queue)
    return " [x] Sent CodePushed"

@bp.route("/repo/", methods=['POST'])
def repo_added():
    payload = request.get_json(force=True)
    performed_by = events_pb2.ScmUser(id=payload['performed_by']['id'],
                              username=payload['performed_by']['user_name'],
                              email=payload['performed_by']['email'])
    rabbitmq = get_rabbitmq()
    ts = timestamp_from_json_string(payload['timestamp'])
    event = events_pb2.RepositoryAdded(identifier=events_pb2.RepoIdentifier(
                                    short_name=payload['identifier']['short_name'],
                                    full_name=payload['identifier']['full_name'],
                                    repo_type=payload['identifier']['repo_type']
                                  ),
                                  description=payload['description'],
                                  html_url=payload['html_url'],
                                  api_url=payload['api_url'],
                                  performed_by=performed_by,
                                  timestamp=ts)

    queue = queue_configs.EXTERNAL_QUEUES['scm.repo.create']
    publish_to_queue(rabbitmq, event, queue)
    return " [x] Sent RepoAdded"

@bp.route("/repo/", methods=['DELETE'])
def repo_removed():
    payload = request.get_json(force=True)
    performed_by = events_pb2.ScmUser(id=payload['performed_by']['id'],
                              username=payload['performed_by']['user_name'],
                              email=payload['performed_by']['email'])

    rabbitmq = get_rabbitmq()
    ts = timestamp_from_json_string(payload['timestamp'])
    event = events_pb2.RepositoryRemoved(identifier=events_pb2.RepoIdentifier(
                                            short_name=payload['identifier']['short_name'],
                                            full_name=payload['identifier']['full_name'],
                                            repo_type=payload['identifier']['repo_type']
                                          ),
                                          performed_by=performed_by,
                                          timestamp=ts)

    queue = queue_configs.EXTERNAL_QUEUES['scm.repo.remove']
    publish_to_queue(rabbitmq, event, queue)
    return " [x] Sent RepoRemoved"

@bp.route("/pull_request/open/", methods=['POST'])
def pull_request_opened():
    payload = request.get_json(force=True)
    opened_by = events_pb2.ScmUser(id=payload['opened_by']['id'],
                              username=payload['opened_by']['user_name'],
                              email=payload['opened_by']['email'])

    rabbitmq = get_rabbitmq()
    ts = timestamp_from_json_string(payload['timestamp'])
    event = events_pb2.PullRequestOpened(id=payload['id'],
                                         pr_repo=events_pb2.RepoIdentifier(
                                             short_name=payload['pr_repo']['short_name'],
                                             full_name=payload['pr_repo']['full_name'],
                                             repo_type=payload['pr_repo']['repo_type']
                                         ),
                                         head_sha=payload['head_sha'],
                                         opened_by=opened_by,
                                         base_sha=payload['base_sha'],
                                         base_repo=events_pb2.RepoIdentifier(
                                             short_name=payload['base_repo']['short_name'],
                                             full_name=payload['base_repo']['full_name'],
                                             repo_type=payload['base_repo']['repo_type']
                                         ),
                                         html_url=payload['html_url'],
                                         api_url=payload['api_url'],
                                         timestamp=ts)

    queue = queue_configs.EXTERNAL_QUEUES['scm.pull_request.open']
    publish_to_queue(rabbitmq, event, queue)
    return " [x] Sent PullRequestOpened"

@bp.route("/pull_request/close/", methods=['POST'])
def pull_request_closed():
    payload = request.get_json(force=True)
    closed_by = events_pb2.ScmUser(id=payload['closed_by']['id'],
                              username=payload['closed_by']['user_name'],
                              email=payload['closed_by']['email'])

    rabbitmq = get_rabbitmq()
    ts = timestamp_from_json_string(payload['timestamp'])
    event = events_pb2.PullRequestClosed(id=payload['id'],
                                         pr_repo=events_pb2.RepoIdentifier(
                                             short_name=payload['pr_repo']['short_name'],
                                             full_name=payload['pr_repo']['full_name'],
                                             repo_type=payload['pr_repo']['repo_type']
                                         ),
                                         closed_by=closed_by,
                                         timestamp=ts)

    queue = queue_configs.EXTERNAL_QUEUES['scm.pull_request.close']
    publish_to_queue(rabbitmq, event, queue)
    return " [x] Sent PullRequestClosed"

@bp.route("/code_review_completed/", methods=['POST'])
def code_review_completed():
    payload = request.get_json(force=True)
    completed_by = events_pb2.ScmUser(id=payload['completed_by']['id'],
                              username=payload['completed_by']['user_name'],
                              email=payload['completed_by']['email'])

    rabbitmq = get_rabbitmq()
    ts = timestamp_from_json_string(payload['timestamp'])
    event = events_pb2.CodeReviewCompleted(pr_id=payload['id'],
                                           pr_repo=events_pb2.RepoIdentifier(
                                               short_name=payload['pr_repo']['short_name'],
                                               full_name=payload['pr_repo']['full_name'],
                                               repo_type=payload['pr_repo']['repo_type']
                                           ),
                                           result=events_pb2.CodeReviewResult.Value(payload['result']),
                                           completed_by=completed_by,
                                           timestamp=ts)

    queue = queue_configs.EXTERNAL_QUEUES['scm.code_review.complete']
    publish_to_queue(rabbitmq, event, queue)
    return " [x] Sent CodeReviewCompleted"
