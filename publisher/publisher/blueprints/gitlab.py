from flask import Blueprint, request, session, g, redirect, url_for, abort, \
     render_template, flash, current_app
from ngcd_common import events_pb2, queue_configs
from google.protobuf.timestamp_pb2 import Timestamp
from kombu import Connection
import datetime
from random import randint

# create our blueprint :)
bp = Blueprint('gitlab', __name__, url_prefix='/gitlab')

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

def handle_push(payload):
    commits = []
    if 'commits' in payload:
        for commit in payload['commits']:
            commits.append(events_pb2.ScmCommit(sha=commit['id'],
                                                message=commit['message'],
                                                author=events_pb2.ScmUser(username=commit['author']['name'],
                                                                          email=commit['author']['email']),
                                                timestamp=timestamp_from_json_string(commit['timestamp'])))
    now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    event = events_pb2.CodePushed(identifier=events_pb2.RepoIdentifier(
                                    short_name=payload['project']['name'],
                                    full_name=payload['project']['path_with_namespace'],
                                    repo_type=events_pb2.GITLAB
                                  ),
                                  new_head_sha=payload['after'],
                                  previous_head_sha=payload['before'],
                                  target_branch=payload['ref'],
                                  pusher=events_pb2.ScmUser(id=str(payload['user_id']),
                                                            username=payload['user_username'],
                                                            email=payload['user_email']),
                                  commits=commits,
                                  timestamp=timestamp_from_json_string(now))

    return (queue_configs.EXTERNAL_QUEUES['scm.repo.push'], event)

def handle_merge_request(payload):
    action = payload['object_attributes']['state']
    if action == 'opened':
        return _handle_opened_merge_request(payload)
    elif action == 'closed':
        return _handle_closed_merge_request(payload)
    else:
        print('Dont know how to handle state [{}]'.format(action))
        return (None, None)

def _handle_opened_merge_request(payload):
    opened_by = events_pb2.ScmUser(id=str(payload['object_attributes']['author_id']),
                                   username=payload['user']['username'])
    now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    event = events_pb2.PullRequestOpened(id=str(payload['object_attributes']['id']),
                                         pr_repo=events_pb2.RepoIdentifier(
                                             short_name=payload['project']['name'],
                                             full_name=payload['project']['path_with_namespace'],
                                             repo_type=events_pb2.GITLAB
                                         ),
                                         head_sha=payload['object_attributes']['last_commit']['id'],
                                         opened_by=opened_by,
                                         base_sha=None,
                                         base_repo=events_pb2.RepoIdentifier(
                                             short_name=payload['object_attributes']['source']['name'],
                                             full_name=payload['object_attributes']['source']['path_with_namespace'],
                                             repo_type=events_pb2.GITLAB
                                         ),
                                         html_url=payload['object_attributes']['url'],
                                         api_url=None,
                                         timestamp=timestamp_from_json_string(now))
    return (queue_configs.EXTERNAL_QUEUES['scm.pull_request.open'], event)

def _handle_closed_merge_request(payload):
    closed_by = events_pb2.ScmUser(id=str(payload['object_attributes']['author_id']),
                                   username=payload['user']['username'])

    now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    event = events_pb2.PullRequestClosed(id=str(payload['object_attributes']['id']),
                                         pr_repo=events_pb2.RepoIdentifier(
                                             short_name=payload['project']['name'],
                                             full_name=payload['project']['path_with_namespace'],
                                             repo_type=events_pb2.GITLAB
                                         ),
                                         closed_by=closed_by,
                                         timestamp=timestamp_from_json_string(now))
    return (queue_configs.EXTERNAL_QUEUES['scm.pull_request.close'], event)

def handle_repo_updated(payload):
    action = payload['event_name']
    if action == 'project_create':
        return _handle_repo_created(payload)
    elif action == 'project_destroy':
        return _handle_repo_removed(payload)
    else:
        current_app.logger.debug('Dont know how to handle event type [{}]'.format(action))
        return (None, None)

def _handle_repo_created(payload):
    performed_by = events_pb2.ScmUser(email=payload['owner_email'])

    ts = timestamp_from_json_string(payload['created_at'])
    event = events_pb2.RepositoryAdded(identifier=events_pb2.RepoIdentifier(
                                    short_name=payload['name'],
                                    full_name=payload['path_with_namespace'],
                                    repo_type=events_pb2.GITLAB
                                  ),
                                  description='',
                                  html_url='',
                                  api_url='',
                                  performed_by=performed_by,
                                  timestamp=ts)

    return (queue_configs.EXTERNAL_QUEUES['scm.repo.create'], event)

def _handle_repo_removed(payload):
    performed_by = events_pb2.ScmUser(email=payload['owner_email'])

    ts = timestamp_from_json_string(payload['updated_at'])
    event = events_pb2.RepositoryRemoved(identifier=events_pb2.RepoIdentifier(
                                            short_name=payload['name'],
                                            full_name=payload['path_with_namespace'],
                                            repo_type=events_pb2.GITLAB
                                          ),
                                          performed_by=performed_by,
                                          timestamp=ts)
    return (queue_configs.EXTERNAL_QUEUES['scm.repo.remove'], event)

HOOK_HANDLERS = {
    'Push Hook': handle_push,
    'Merge Request Hook': handle_merge_request,
    'System Hook': handle_repo_updated
}

@bp.route("/", methods=['POST'])
def webhook():
    payload = request.get_json(force=True)
    event_type = request.headers.get('X-Gitlab-Event')
    if event_type not in HOOK_HANDLERS:
        current_app.logger.debug('Not caring about event type [{}]'.format(event_type))
        return 'OK'

    current_app.logger.debug('Handling event type [{}]'.format(event_type))
    handler_func = HOOK_HANDLERS[event_type]
    handler_func(payload)
    rabbitmq = get_rabbitmq()

    (queue, event) = handler_func(payload)
    if queue and event:
        publish_to_queue(rabbitmq, event, queue)

    return "OK"
