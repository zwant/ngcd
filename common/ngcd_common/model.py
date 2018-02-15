import pytz
import json
from ngcd_common import getLogger
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMP
from google.protobuf.json_format import MessageToDict
from sqlalchemy import Column, Integer, String, DateTime, func, Boolean, types
from sqlalchemy.ext.declarative import declarative_base
import dateutil.parser

ProjectionBase = declarative_base()
EventBase = declarative_base()

class StringyJSON(types.TypeDecorator):
    """Stores and retrieves JSON as TEXT."""

    impl = types.TEXT

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


# TypeEngine.with_variant says "use StringyJSON instead when
# connecting to 'sqlite'"
AdaptableJSONB = JSONB().with_variant(StringyJSON, 'sqlite')

class Pipeline(ProjectionBase):
    __tablename__ = 'pipelines'
    id = Column(Integer, primary_key=True)
    external_id = Column(String, nullable=False, index=True)
    currently_running = Column(Boolean, nullable=False)
    result = Column(String, nullable=True)
    last_update = Column(TIMESTAMP(timezone=True), nullable=False)
    started_running_at = Column(TIMESTAMP(timezone=True), nullable=True)
    finished_running_at = Column(TIMESTAMP(timezone=True), nullable=True)
    last_duration = Column(Integer, nullable=True)
    number_of_runs = Column(Integer, nullable=True)
    average_duration = Column(Integer, nullable=True)

    def __init__(self, external_id, id=None, currently_running=False, result=None, last_update=None,
                 started_running_at=None, finished_running_at=None, last_duration=None, number_of_runs=0,
                 average_duration=None):
        self.id = id
        self.external_id = external_id
        self.currently_running = currently_running
        self.result = result
        self.last_update = last_update
        self.started_running_at = started_running_at
        self.finished_running_at = finished_running_at
        self.last_duration = last_duration
        self.number_of_runs = number_of_runs
        self.average_duration = average_duration

    def __repr__(self):
        return '<Pipeline {}>, last_update: {}, currently_running: {}, result: {}, last_duration: {}, number_of_runs: {}, average_duration: {}'.format(
        self.external_id,
        self.last_update,
        self.currently_running,
        self.result,
        self.last_duration,
        self.number_of_runs,
        self.average_duration)

    def as_dict(self):
        return {
            'id': self.id,
            'external_id': self.external_id,
            'last_update': self.last_update.isoformat(),
            'currently_running': self.currently_running,
            'result': self.result,
            'number_of_runs': self.number_of_runs,
            'started_running_at': self.started_running_at.isoformat() if self.started_running_at else None,
            'finished_running_at': self.finished_running_at.isoformat() if self.finished_running_at else None,
            'average_duration': self.average_duration,
            'last_duration': self.last_duration
        }

class PipelineStage(ProjectionBase):
    __tablename__ = 'pipeline_stages'
    id = Column(Integer, primary_key=True)
    external_id = Column(String, nullable=False, index=True)
    pipeline_id = Column(String, nullable=False)
    currently_running = Column(Boolean, nullable=False, server_default='false')
    result = Column(String, nullable=True)
    last_update = Column(TIMESTAMP(timezone=True), nullable=False)
    started_running_at = Column(TIMESTAMP(timezone=True), nullable=True)
    finished_running_at = Column(TIMESTAMP(timezone=True), nullable=True)
    number_of_runs = Column(Integer, nullable=True)
    average_duration = Column(Integer, nullable=True)
    last_duration = Column(Integer, nullable=True)

    def __init__(self, external_id, id=None, pipeline_id=None, currently_running=False, result=None, last_update=None,
                 started_running_at=None, finished_running_at=None, last_duration=None, number_of_runs=0,
                 average_duration=None):
        self.id = id
        self.external_id = external_id
        self.pipeline_id = pipeline_id
        self.currently_running = currently_running
        self.result = result
        self.last_update = last_update
        self.started_running_at = started_running_at
        self.finished_running_at = finished_running_at
        self.last_duration = last_duration
        self.number_of_runs = number_of_runs
        self.average_duration = average_duration

    def __repr__(self):
        return '<PipelineStage {}> pipeline_id: {}, last_update: {}, currently_running: {}, result: {}, number_of_runs: {}, average_duration: {}, last_duration: {}'.format(
        self.external_id,
        self.pipeline_id,
        self.last_update,
        self.currently_running,
        self.result,
        self.number_of_runs,
        self.average_duration,
        self.last_duration)

    def as_dict(self):
        return {
            'id': self.id,
            'external_id': self.external_id,
            'pipeline_id': self.pipeline_id,
            'last_update': self.last_update.isoformat(),
            'currently_running': self.currently_running,
            'result': self.result,
            'started_running_at': self.started_running_at.isoformat() if self.started_running_at else None,
            'finished_running_at': self.finished_running_at.isoformat() if self.finished_running_at else None,
            'number_of_runs': self.number_of_runs,
            'average_duration': self.average_duration,
            'last_duration': self.last_duration
        }

class Repository(ProjectionBase):
    __tablename__ = 'repositories'
    id = Column(Integer, primary_key=True)
    external_id = Column(String, nullable=False, index=True)
    is_deleted = Column(Boolean, nullable=False, index=True)
    short_name = Column(String, nullable=False)
    full_name = Column(String, nullable=False, unique=True, index=True)
    type = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    html_url = Column(String, nullable=True)
    api_url = Column(String, nullable=True)
    created_by = Column(AdaptableJSONB, nullable=True)
    deleted_by = Column(AdaptableJSONB, nullable=True)
    last_pusher = Column(AdaptableJSONB, nullable=True)
    head_sha = Column(String, nullable=True)
    previous_head_sha = Column(String, nullable=True)
    last_update = Column(TIMESTAMP(timezone=True), nullable=False)
    commits = Column(AdaptableJSONB, nullable=True, index=True)

    def __init__(self,
                 external_id,
                 id=None,
                 is_deleted=False,
                 short_name=None,
                 full_name=None,
                 type=None,
                 description=None,
                 html_url=None,
                 api_url=None,
                 created_by=None,
                 deleted_by=None,
                 last_pusher=None,
                 head_sha=None,
                 previous_head_sha=None,
                 last_update=None,
                 commits=None):
        self.id = id
        self.external_id = external_id
        self.is_deleted = is_deleted
        self.short_name = short_name
        self.full_name = full_name
        self.type = type
        self.description = description
        self.html_url = html_url
        self.api_url = api_url
        self.created_by = created_by
        self.deleted_by = deleted_by
        self.last_pusher = last_pusher
        self.head_sha = head_sha
        self.previous_head_sha = previous_head_sha
        self.last_update = last_update
        if commits == None:
            self.commits = []
        else:
            self.commits = commits

    def __repr__(self):
        return '<Repository {}> is_deleted: {}, full_name: {}, short_name: {}, last_update: {}, last_pusher: {}, head_sha: {}, previous_head_sha: {}'.format(
        self.external_id,
        self.is_deleted,
        self.full_name,
        self.short_name,
        self.last_update,
        self.last_pusher,
        self.head_sha,
        self.previous_head_sha)

    def as_dict(self):
        return {
            'id': self.id,
            'external_id': self.external_id,
            'short_name': self.short_name,
            'full_name': self.full_name,
            'type': self.type,
            'is_deleted': self.is_deleted,
            'html_url': self.html_url,
            'api_url': self.api_url,
            'last_update': self.last_update.isoformat(),
            'last_pusher': self.last_pusher,
            'head_sha': self.head_sha,
            'previous_head_sha': self.previous_head_sha,
            'commits': self.commits
        }

class Event(EventBase):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False, index=True)
    body = Column(AdaptableJSONB, nullable=False, index=True)
    inserted_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    event_origin_time = Column(TIMESTAMP(timezone=True), nullable=False)

    def __repr__(self):
        return '<Event {}> Type: {}, inserted_at: {}, event_origin_time: {}. Body: {}, '.format(self.id,
        self.type, self.inserted_at, self.event_origin_time, self.body)

    @classmethod
    def write_event(cls, session, event_pb):
        event_model = Event(type=type(event_pb).__name__,
                            body=MessageToDict(event_pb, including_default_value_fields=True),
                            event_origin_time=cls._get_event_origin_time(event_pb))
        getLogger().debug('Saving Event: {}'.format(event_model))
        session.add(event_model)
        session.commit()

    @classmethod
    def _get_event_external_id(cls, event_pb):
        return event_pb.uuid

    @classmethod
    def _get_event_origin_time(cls, event_pb):
        ts_string = event_pb.timestamp.ToJsonString()
        return dateutil.parser.parse(ts_string)
