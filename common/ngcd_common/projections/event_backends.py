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
                    .order_by(Event.event_origin_time.asc(), Event.id.asc())
