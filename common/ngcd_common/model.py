import pytz

from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMP
from google.protobuf.json_format import MessageToDict
from sqlalchemy import Column, Integer, String, DateTime, func, Boolean
from sqlalchemy.ext.declarative import declarative_base
import dateutil.parser

Base = declarative_base()

class Pipeline(Base):
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

    def __init__(self, external_id, currently_running=False, result=None, last_update=None,
                 started_running_at=None, finished_running_at=None, last_duration=None, number_of_runs=0,
                 average_duration=None):
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
            'last_update': self.last_update,
            'currently_running': self.currently_running,
            'result': self.result,
            'number_of_runs': self.number_of_runs,
            'started_running_at': self.started_running_at,
            'finished_running_at': self.finished_running_at,
            'average_duration': self.average_duration,
            'last_duration': self.last_duration
        }

class PipelineStage(Base):
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

    def __init__(self, external_id, pipeline_id=None, currently_running=False, result=None, last_update=None,
                 started_running_at=None, finished_running_at=None, last_duration=None, number_of_runs=0,
                 average_duration=None):
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
            'last_update': self.last_update,
            'currently_running': self.currently_running,
            'result': self.result,
            'started_running_at': self.started_running_at,
            'finished_running_at': self.finished_running_at,
            'number_of_runs': self.number_of_runs,
            'average_duration': self.average_duration,
            'last_duration': self.last_duration
        }

class Repository(Base):
    __tablename__ = 'repositories'
    id = Column(Integer, primary_key=True)
    external_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    last_pusher = Column(JSONB, nullable=False)
    head_sha = Column(String, nullable=False)
    previous_head_sha = Column(String, nullable=False)
    last_update = Column(TIMESTAMP(timezone=True), nullable=False)
    commits = Column(JSONB, nullable=False, index=True)

    def __repr__(self):
        return '<Repository {}> name: {}, last_update: {}, last_pusher: {}, head_sha: {}, previous_head_sha: {}'.format(
        self.external_id,
        self.name,
        self.last_update,
        self.last_pusher,
        self.head_sha,
        self.previous_head_sha)

    def as_dict(self):
        return {
            'id': self.id,
            'external_id': self.external_id,
            'name': self.name,
            'last_update': self.last_update,
            'last_pusher': self.last_pusher,
            'head_sha': self.head_sha,
            'previous_head_sha': self.previous_head_sha,
            'commits': self.commits
        }

class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False, index=True)
    body = Column(JSONB, nullable=False, index=True)
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
        print('Saving Event: {}'.format(event_model))
        session.add(event_model)
        session.commit()

    @classmethod
    def _get_event_external_id(cls, event_pb):
        return event_pb.uuid

    @classmethod
    def _get_event_origin_time(cls, event_pb):
        ts_string = event_pb.timestamp.ToJsonString()
        return dateutil.parser.parse(ts_string)
