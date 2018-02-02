from sqlalchemy.dialects.postgresql import UUID, JSONB
from google.protobuf.json_format import MessageToDict
from sqlalchemy import Column, Integer, String, DateTime, func, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Pipeline(Base):
    __tablename__ = 'pipelines'
    id = Column(Integer, primary_key=True)
    external_id = Column(String, nullable=False, index=True)
    currently_running = Column(Boolean, nullable=False, server_default='false')
    result = Column(String, nullable=True)
    last_update = Column(DateTime, nullable=False)
    started_running_at = Column(DateTime, nullable=True)
    finished_running_at = Column(DateTime, nullable=True)

    @classmethod
    def write_projection(cls, session, projection):
        pipeline_model = Pipeline(id=projection.id,
                                  external_id=projection.external_id,
                                  currently_running=projection.currently_running,
                                  result=projection.result,
                                  last_update=projection.last_update,
                                  started_running_at=projection.started_running_at,
                                  finished_running_at=projection.finished_running_at)
        print('Saving Pipeline: {}'.format(pipeline_model))
        session.merge(pipeline_model)
        session.commit()

    def __repr__(self):
        return '<Pipeline {}>, last_update: {}, currently_running: {}, result: {}, '.format(
        self.external_id,
        self.last_update,
        self.currently_running,
        self.result)

    def as_dict(self):
        return {
            'id': self.id,
            'external_id': self.external_id,
            'last_update': self.last_update,
            'currently_running': self.currently_running,
            'result': self.result,
            'started_running_at': self.started_running_at,
            'finished_running_at': self.finished_running_at
        }

class PipelineStage(Base):
    __tablename__ = 'pipeline_stages'
    id = Column(Integer, primary_key=True)
    external_id = Column(String, nullable=False, index=True)
    pipeline_id = Column(String, nullable=False)
    currently_running = Column(Boolean, nullable=False, server_default='false')
    result = Column(String, nullable=True)
    last_update = Column(DateTime, nullable=False)
    started_running_at = Column(DateTime, nullable=True)
    finished_running_at = Column(DateTime, nullable=True)

    @classmethod
    def write_projection(cls, session, projection):
        pipeline_stage_model = PipelineStage(id=projection.id,
                                             external_id=projection.external_id,
                                              currently_running=projection.currently_running,
                                              result=projection.result,
                                              last_update=projection.last_update,
                                              pipeline_id=projection.pipeline_id,
                                              started_running_at=projection.started_running_at,
                                              finished_running_at=projection.finished_running_at)
        print('Saving Pipeline Stage: {}'.format(pipeline_stage_model))
        session.merge(pipeline_stage_model)
        session.commit()

    def __repr__(self):
        return '<PipelineStage {}> pipeline_id: {}, last_update: {}, currently_running: {}, result: {}, '.format(
        self.external_id,
        self.pipeline_id,
        self.last_update,
        self.currently_running,
        self.result)

    def as_dict(self):
        return {
            'id': self.id,
            'external_id': self.external_id,
            'pipeline_id': self.pipeline_id,
            'last_update': self.last_update,
            'currently_running': self.currently_running,
            'result': self.result,
            'started_running_at': self.started_running_at,
            'finished_running_at': self.finished_running_at
        }

class Repository(Base):
    __tablename__ = 'repositories'
    id = Column(Integer, primary_key=True)
    external_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    last_pusher = Column(String, nullable=False)
    head_sha = Column(String, nullable=False)
    previous_head_sha = Column(String, nullable=False)
    last_update = Column(DateTime, nullable=False)

    @classmethod
    def write_projection(cls, session, projection):
        repo_model = Repository(id=projection.id,
                                external_id=projection.external_id,
                                name=projection.name,
                                last_pusher=projection.last_pusher,
                                head_sha=projection.head_sha,
                                previous_head_sha=projection.previous_head_sha,
                                last_update=projection.last_update)
        print('Saving Repository: {}'.format(repo_model))
        session.merge(repo_model)
        session.commit()

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
            'previous_head_sha': self.previous_head_sha
        }

class CodeCommit(Base):
    __tablename__ = 'code_commits'
    id = Column(Integer, primary_key=True)
    sha = Column(String, nullable=False, index=True)
    message = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False)

    def as_dict(self):
        return {
            'id': self.id,
            'sha': self.sha,
            'message': self.message,
            'created_at': self.created_at
        }


class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False, index=True)
    body = Column(JSONB, nullable=False, index=True)
    inserted_at = Column(DateTime, nullable=False, server_default=func.now())
    event_origin_time = Column(DateTime, nullable=False)

    def __repr__(self):
        return '<Event {}> Type: {}, inserted_at: {}, Body: {}, '.format(self.id,
        self.type, self.inserted_at, self.body)

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
        return event_pb.timestamp.ToDatetime()
