from ngcd_common.model import Event

class EventBackend(object):
    def get_all_since(self, after_id):
        """ Should return a generator of Event-model instances, ordered
            by origin time.

        """
        raise NotImplementedError("get_all_since needs to be implemented in inheriting class!")

class SQLAlchemyBackend(EventBackend):
    def __init__(self, db_session):
        from ngcd_common.model import EventBase
        self.db_session = db_session
        EventBase.query = self.db_session.query_property()

    def get_all_since_id(self, after_id):
        return Event.query \
                    .filter(Event.id > after_id) \
                    .order_by(Event.id.asc())

# Note, globally used variables! Not thread safe!
in_memory_events = []
global_id = 0

class DummyBackend(EventBackend):
    fake = None

    def __init__(self):
        global in_memory_events

        from faker import Faker
        self.fake = Faker()
        if not in_memory_events:
            in_memory_events = list(self._generate_pipeline_events())

    def _get_in_memory_events(self):
        global in_memory_events

        return in_memory_events

    def get_all_since_id(self, after_id):
        for event in sorted(self._get_in_memory_events(), key=lambda event: (event.id, event.event_origin_time)):
            if event.id > after_id:
                yield event

    def _next_global_id(self):
        global global_id

        global_id = global_id + 1

        return global_id

    def _generate_pipeline_events(self):
        from ngcd_common import events_pb2
        from google.protobuf.timestamp_pb2 import Timestamp
        from google.protobuf.json_format import MessageToDict
        import random
        from datetime import timedelta
        import pytz

        pipeline_id = 0
        times = self.fake.time_series(start_date="-5d", end_date="now", precision=timedelta(minutes=1), distrib=None, tzinfo=pytz.utc)
        for i in range(0, 10):
            time = next(times)[0].isoformat()
            if i % 2 == 0:
                # Generate started event
                ts = Timestamp()
                ts.FromJsonString(time)
                event_pb = events_pb2.PipelineStarted(uuid=str(pipeline_id),
                                                      timestamp=ts)
                event_model = Event(id=self._next_global_id(),
                                    type='PipelineStarted',
                                    body=MessageToDict(event_pb, including_default_value_fields=True),
                                    event_origin_time=time)



                yield event_model
                yield from self._generate_pipeline_stages(times, pipeline_id)
            else:
                # Generate finished event
                ts = Timestamp()
                ts.FromJsonString(time)
                event_pb = events_pb2.PipelineFinished(uuid=str(pipeline_id),
                                                    timestamp=ts,
                                                    result=random.choice([events_pb2.SUCCESS,
                                                                          events_pb2.FAILURE,
                                                                          events_pb2.ABORTED]),
                                                    duration_ms=random.randint(100, 10000))
                event_model = Event(id=self._next_global_id(),
                                    type='PipelineFinished',
                                    body=MessageToDict(event_pb, including_default_value_fields=True),
                                    event_origin_time=time)

                pipeline_id = pipeline_id + 1

                yield event_model

    def _generate_pipeline_stages(self, time_series, pipeline_id):
        from ngcd_common import events_pb2
        from google.protobuf.timestamp_pb2 import Timestamp
        from google.protobuf.json_format import MessageToDict
        import random
        from datetime import timedelta
        import pytz

        pipeline_stage_id = 0

        for i in range(0, 4):
            time = next(time_series)[0].isoformat()
            if i % 2 == 0:
                # Generate started event
                ts = Timestamp()
                ts.FromJsonString(time)
                event_pb = events_pb2.PipelineStageStarted(uuid=str(pipeline_stage_id),
                                                           pipeline_uuid=str(pipeline_id),
                                                           timestamp=ts)
                event_model = Event(id=self._next_global_id(),
                                    type='PipelineStageStarted',
                                    body=MessageToDict(event_pb, including_default_value_fields=True),
                                    event_origin_time=time)



                yield event_model
            else:
                # Generate finished event
                ts = Timestamp()
                ts.FromJsonString(time)
                event_pb = events_pb2.PipelineStageFinished(uuid=str(pipeline_stage_id),
                                                            pipeline_uuid=str(pipeline_id),
                                                    timestamp=ts,
                                                    result=random.choice([events_pb2.SUCCESS,
                                                                          events_pb2.FAILURE,
                                                                          events_pb2.ABORTED]),
                                                    duration_ms=random.randint(100, 10000))
                event_model = Event(id=self._next_global_id(),
                                    type='PipelineStageFinished',
                                    body=MessageToDict(event_pb, including_default_value_fields=True),
                                    event_origin_time=time)

                pipeline_stage_id = pipeline_stage_id + 1

                yield event_model
