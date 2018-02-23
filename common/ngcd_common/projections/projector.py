from ngcd_common import getLogger
from ngcd_common.model import Event, EventBase
from ngcd_common.projections.projections import Projection
from ngcd_common.projections.projection_backends import SQLAlchemyBackend

class Projector(object):
    event_handling_classes = Projection.__subclasses__()

    last_processed_event_id = 0
    projection_backend = None
    event_backend = None

    def __init__(self, projection_backend, event_backend):
        self.projection_backend = projection_backend
        self.event_backend = event_backend

    def process_events(self, until=10000, only=None):
        i = 0
        for event in self.event_backend.get_all_since_id(self.last_processed_event_id):
            if only and event.id not in only:
                continue
            if i > until:
                return
            getLogger().debug('Processing event [%s] of type [%s]', event.id, event.type)
            self.handle_event(event)
            i = i+1
            self.projection_backend.commit()

    def handle_event(self, event):
        for event_handle_class in self.event_handling_classes:
            if event.type in event_handle_class.get_interesting_events():
                getLogger().debug('Handling event [%s] of type [%s] with class [%s]', event.id, event.type, event_handle_class.__name__)
                event_handle_class().handle_event(self.projection_backend, event)

        self.last_processed_event_id = event.id
