from ngcd_common.model import Event
from ngcd_common.projections import Projection, PipelineProjection, PipelineStageProjection, RepositoryProjection

class Projector(object):
    event_handling_classes = [PipelineProjection, PipelineStageProjection, RepositoryProjection]
    last_processed_event_id = 0
    db_session = None

    def __init__(self, db_session):
        self.db_session = db_session

    def process_events(self, until=10000):
        query = Event.query \
                    .filter(Event.id > self.last_processed_event_id) \
                    .order_by(Event.event_origin_time.asc())
        i = 0
        for event in query.all():
            if i > until:
                return
            print('Processing event {}'.format(event.id))
            self.handle_event(event)
            i = i+1

    def handle_event(self, event):
        for event_handle_class in self.event_handling_classes:
            if event.type in event_handle_class.get_interesting_events():
                curr_class_name = event_handle_class.__name__
                the_id = event_handle_class.get_external_id_from_body(event.body)
                entity = event_handle_class.get_db_model().query \
                            .filter(event_handle_class.get_db_model().external_id==the_id).first()
                new_entity = event_handle_class.handle_event(entity, event)

                event_handle_class.get_db_model().write_projection(self.db_session, new_entity)
        self.last_processed_event_id = event.id
