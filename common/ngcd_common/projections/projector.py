from ngcd_common import getLogger
from ngcd_common.model import Event
from ngcd_common.projections.projections import Projection
from ngcd_common.projections.backends import PostgresBackend

class Projector(object):
    event_handling_classes = Projection.__subclasses__()

    last_processed_event_id = 0
    backend = None

    def __init__(self, backend):
        self.backend = backend

    def process_events(self, until=10000, only=None):
        query = Event.query \
                    .filter(Event.id > self.last_processed_event_id) \
                    .order_by(Event.event_origin_time.asc(), Event.id.asc())

        i = 0
        for event in query.all():
            if only and event.id not in only:
                continue
            if i > until:
                return
            getLogger().debug('Processing event [%s] of type [%s]', event.id, event.type)
            self.handle_event(event)
            i = i+1
            self.backend.commit()

    def handle_event(self, event):
        for event_handle_class in self.event_handling_classes:
            if event.type in event_handle_class.get_interesting_events():
                getLogger().debug('Handling event [%s] of type [%s] with class [%s]', event.id, event.type, event_handle_class.__name__)
                event_handle_class().handle_event(self.backend, event)

        self.last_processed_event_id = event.id
