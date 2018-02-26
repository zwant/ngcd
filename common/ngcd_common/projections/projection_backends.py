class ProjectionBackend(object):
    def get_all(self, model):
        raise NotImplementedError("get_all needs to be implemented in inheriting class!")

    def get_by_external_id(self, external_id, model):
        raise NotImplementedError("get_by_external_id needs to be implemented in inheriting class!")

    def get_one_by_external_id(self, external_id, model):
        raise NotImplementedError("get_one_by_external_id needs to be implemented in inheriting class!")

    def get_or_create_by_external_id(self, external_id, model):
        raise NotImplementedError("get_or_create_by_external_id needs to be implemented in inheriting class!")

    def get_by_filter(self, model, filters):
        raise NotImplementedError("get_by_filter needs to be implemented in inheriting class!")

    def get_one_by_filter(self, model, filters):
        raise NotImplementedError("get_one_by_filter needs to be implemented in inheriting class!")

    def get_or_create_by_filter(self, external_id, model, filters):
        raise NotImplementedError("get_or_create_by_filter needs to be implemented in inheriting class!")

    def save(self, model):
        raise NotImplementedError("save needs to be implemented in inheriting class!")

    def commit(self):
        raise NotImplementedError("commit needs to be implemented in inheriting class!")

# Note:
# Globally used variables, not thread safe!
from collections import defaultdict
global_data = defaultdict(list)
last_id = 0

class InMemoryBackend(ProjectionBackend):
    def __init__(self, empty=False):
        if empty:
            global global_data
            global_data = defaultdict(list)
    def _get_next_id(self):
        global last_id
        last_id = last_id + 1
        return last_id

    def _get_data(self):
        global global_data
        return global_data

    def get_all(self, model):
        return self._get_data()[model.__table__.name]

    def get_by_external_id(self, external_id, model):
        found = []
        for thing in self._get_data()[model.__table__.name]:
            if thing.external_id == external_id:
                found.append(thing)
        return found

    def get_one_by_external_id(self, external_id, model):
        found = self.get_by_external_id(external_id, model)
        return found[0] if found else None

    def get_by_filter(self, model, filters):
        found = []
        for thing in self._get_data()[model.__table__.name]:
            matches = True
            for key, value in filters.items():
                if getattr(thing, key) != value:
                    matches = False
                    break
            if matches:
                found.append(thing)
        return found

    def get_one_by_filter(self, model, filters):
        found = self.get_by_filter(model, filters)
        return found[0] if found else None

    def get_or_create_by_external_id(self, external_id, model):
        found = self.get_one_by_external_id(external_id, model)
        if found:
            return found
        return model(id=self._get_next_id(), external_id=external_id)

    def get_or_create_by_filter(self, external_id, model, filters):
        found = self.get_one_by_filter(model, filters)
        if found:
            return found
        return model(id=self._get_next_id(), external_id=external_id)

    def save(self, model):
        for thing in self._get_data()[model.__table__.name]:
            if thing.id == model.id:
                thing = model
                return
        self._get_data()[model.__table__.name].append(model)

    def commit(self):
        pass

class SQLAlchemyBackend(ProjectionBackend):
    def __init__(self, db_session):
        self.db_session = db_session

    def get_all(self, model):
        return model.query.all()

    def get_by_external_id(self, external_id, model):
        return self.get_by_filter(model, {'external_id': external_id})

    def get_one_by_external_id(self, external_id, model):
        return self.get_one_by_filter(model, {'external_id': external_id})

    def get_by_filter(self, model, filters):
        query = model.query.filter_by(**filters)
        return query.all()

    def get_one_by_filter(self, model, filters):
        query = model.query.filter_by(**filters)
        return query.first()

    def get_or_create_by_external_id(self, external_id, model):
        retrieved_model = self.get_one_by_external_id(external_id, model)
        if not retrieved_model:
            retrieved_model = model(external_id=external_id)

        return retrieved_model

    def get_or_create_by_filter(self, external_id, model, filters):
        retrieved_model = self.get_one_by_filter(model, filters)
        if not retrieved_model:
            retrieved_model = model(external_id=external_id)

        return retrieved_model

    def save(self, model):
        self.db_session.merge(model)

    def commit(self):
        self.db_session.commit()
