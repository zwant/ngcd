from ngcd_common.projections.projections import RepositoryProjection
from ngcd_common.model import Repository as RepositoryModel
import dateutil.parser

class Container(object):
    pass

def apply_events(func, model, events):
    for event in events:
        func(model, event)

class TestRepositoryProjection(object):
    def test_apply_single_added_event_to_empty(self):
        event = Container()
        event.type = 'RepositoryAdded'
        event.body = {
            'identifier': {
                'shortName': 'test-repo',
                'fullName': 'test-org/test-repo',
                'repoType': 'GITHUB_ENTERPRISE'
            },
            'description': 'A great test repo',
            'htmlUrl': 'http://someurl',
            'apiUrl': 'http://apiurl',
            'performedBy': {
                'id': '1',
                'userName': 'test-user',
                'email': 'test-email'
            },
            'timestamp': '2017-02-02T14:25:43.511Z'
        }
        model = RepositoryModel(external_id='test-org/test-repo')
        projection = RepositoryProjection()
        apply_events(projection.apply_event_to_model,
                     model,
                     [event])

        assert model.external_id == 'test-org/test-repo'
        assert model.short_name == 'test-repo'
        assert model.full_name == 'test-org/test-repo'
        assert model.type == 'GITHUB_ENTERPRISE'
        assert model.head_sha == None
        assert model.previous_head_sha == None
        assert len(model.commits) == 0
        assert model.last_pusher == None
        assert model.description == 'A great test repo'
        assert model.html_url == 'http://someurl'
        assert model.api_url == 'http://apiurl'
        assert model.is_deleted == False
        assert model.created_by == {
            'id': '1',
            'userName': 'test-user',
            'email': 'test-email'
        }
        assert model.last_update == dateutil.parser.parse('2017-02-02T14:25:43.511Z')

    def test_create_then_remove_repository(self):
        event = Container()
        event.type = 'RepositoryAdded'
        event.body = {
            'identifier': {
                'shortName': 'test-repo',
                'fullName': 'test-org/test-repo',
                'repoType': 'GITHUB_ENTERPRISE'
            },
            'description': 'A great test repo',
            'htmlUrl': 'http://someurl',
            'apiUrl': 'http://apiurl',
            'performedBy': {
                'id': '1',
                'userName': 'test-user',
                'email': 'test-email'
            },
            'timestamp': '2017-02-02T14:25:43.511Z'
        }

        event2 = Container()
        event2.type = 'RepositoryRemoved'
        event2.body = {
            'identifier': {
                'shortName': 'test-repo',
                'fullName': 'test-org/test-repo',
                'repoType': 'GITHUB_ENTERPRISE'
            },
            'performedBy': {
                'id': '2',
                'userName': 'other-user',
                'email': 'other-email'
            },
            'timestamp': '2017-02-03T14:25:43.511Z'
        }
        model = RepositoryModel(external_id='test-org/test-repo')
        projection = RepositoryProjection()
        apply_events(projection.apply_event_to_model,
                     model,
                     [event, event2])

        assert model.external_id == 'test-org/test-repo'
        assert model.short_name == 'test-repo'
        assert model.full_name == 'test-org/test-repo'
        assert model.type == 'GITHUB_ENTERPRISE'
        assert model.head_sha == None
        assert model.previous_head_sha == None
        assert len(model.commits) == 0
        assert model.last_pusher == None
        assert model.description == 'A great test repo'
        assert model.html_url == 'http://someurl'
        assert model.api_url == 'http://apiurl'
        assert model.is_deleted == True
        assert model.created_by == {
            'id': '1',
            'userName': 'test-user',
            'email': 'test-email'
        }

        assert model.deleted_by == {
            'id': '2',
            'userName': 'other-user',
            'email': 'other-email'
        }
        assert model.last_update == dateutil.parser.parse('2017-02-03T14:25:43.511Z')

    def test_create_commit_then_remove_repository(self):
        event = Container()
        event.type = 'RepositoryAdded'
        event.body = {
            'identifier': {
                'shortName': 'test-repo',
                'fullName': 'test-org/test-repo',
                'repoType': 'GITHUB_ENTERPRISE'
            },
            'description': 'A great test repo',
            'htmlUrl': 'http://someurl',
            'apiUrl': 'http://apiurl',
            'performedBy': {
                'id': '1',
                'userName': 'test-user',
                'email': 'test-email'
            },
            'timestamp': '2017-02-02T14:25:43.511Z'
        }

        event2 = Container()
        event2.type = 'CodePushed'
        event2.body = {
            'identifier': {
                'shortName': 'test-repo',
                'fullName': 'test-org/test-repo',
                'repoType': 'GITHUB_ENTERPRISE'
            },
            'newHeadSha': '2',
            'previousHeadSha': '1',
            'pusher': 'test-user',
            'commits': [{"test_commit": "hej"}],
            'timestamp': '2017-02-02T14:28:43.511Z'
        }

        event3 = Container()
        event3.type = 'RepositoryRemoved'
        event3.body = {
            'identifier': {
                'shortName': 'test-repo',
                'fullName': 'test-org/test-repo',
                'repoType': 'GITHUB_ENTERPRISE'
            },
            'performedBy': {
                'id': '2',
                'userName': 'other-user',
                'email': 'other-email'
            },
            'timestamp': '2017-02-02T14:25:43.511Z'
        }
        model = RepositoryModel(external_id='test-org/test-repo')
        projection = RepositoryProjection()
        apply_events(projection.apply_event_to_model,
                     model,
                     [event, event2, event3])

        assert model.external_id == 'test-org/test-repo'
        assert model.short_name == 'test-repo'
        assert model.full_name == 'test-org/test-repo'
        assert model.type == 'GITHUB_ENTERPRISE'
        assert model.head_sha == '2'
        assert model.previous_head_sha == '1'
        assert len(model.commits) == 1
        assert model.last_pusher == 'test-user'
        assert model.description == 'A great test repo'
        assert model.html_url == 'http://someurl'
        assert model.api_url == 'http://apiurl'
        assert model.is_deleted == True
        assert model.created_by == {
            'id': '1',
            'userName': 'test-user',
            'email': 'test-email'
        }

        assert model.deleted_by == {
            'id': '2',
            'userName': 'other-user',
            'email': 'other-email'
        }
        assert model.last_update == dateutil.parser.parse('2017-02-02T14:25:43.511Z')

    def test_apply_single_code_pushed_event_to_empty(self):
        event = Container()
        event.type = 'CodePushed'
        event.body = {
            'identifier': {
                'shortName': 'test-repo',
                'fullName': 'test-org/test-repo',
                'repoType': 'GITHUB_ENTERPRISE'
            },
            'newHeadSha': '2',
            'previousHeadSha': '1',
            'pusher': 'test-user',
            'commits': [{"test_commit": "hej"}],
            'timestamp': '2017-02-02T14:25:43.511Z'
        }
        model = RepositoryModel(external_id='test')
        apply_events(RepositoryProjection.apply_event_to_model,
                     model,
                     [event])

        assert model.external_id == 'test'
        assert model.short_name == 'test-repo'
        assert model.full_name == 'test-org/test-repo'
        assert model.type == 'GITHUB_ENTERPRISE'
        assert model.head_sha == '2'
        assert model.previous_head_sha == '1'
        assert len(model.commits) == 1
        assert model.last_pusher == 'test-user'
        assert model.last_update == dateutil.parser.parse('2017-02-02T14:25:43.511Z')

    def test_apply_multiple_code_pushed_events_to_empty(self):
        event1 = Container()
        event1.type = 'CodePushed'
        event1.body = {
            'identifier': {
                'shortName': 'test-repo',
                'fullName': 'test-org/test-repo',
                'repoType': 'GITHUB_ENTERPRISE'
            },
            'newHeadSha': '2',
            'previousHeadSha': '1',
            'pusher': 'test-user',
            'commits': [{"test_commit": "hej"}],
            'timestamp': '2017-02-02T14:25:43.511Z'
        }

        event2 = Container()
        event2.type = 'CodePushed'
        event2.body = {
            'identifier': {
                'shortName': 'test-repo',
                'fullName': 'test-org/test-repo',
                'repoType': 'GITHUB_ENTERPRISE'
            },
            'newHeadSha': '3',
            'previousHeadSha': '2',
            'pusher': 'test-user',
            'commits': [{"test_commit2": "hej"}],
            'timestamp': '2017-02-02T15:25:43.511Z'
        }

        model = RepositoryModel(external_id='test')
        apply_events(RepositoryProjection.apply_event_to_model,
                     model,
                     [event1, event2])

        assert model.external_id == 'test'
        assert model.short_name == 'test-repo'
        assert model.full_name == 'test-org/test-repo'
        assert model.type == 'GITHUB_ENTERPRISE'
        assert model.head_sha == '3'
        assert model.previous_head_sha == '2'
        assert len(model.commits) == 2
        assert model.last_pusher == 'test-user'
        assert model.last_update == dateutil.parser.parse('2017-02-02T15:25:43.511Z')

    def test_apply_single_code_pushed_event_to_pre_existing(self):
        event1 = Container()
        event1.type = 'CodePushed'
        event1.body = {
            'identifier': {
                'shortName': 'test-repo',
                'fullName': 'test-org/test-repo',
                'repoType': 'GITHUB_ENTERPRISE'
            },
            'newHeadSha': '2',
            'previousHeadSha': '1',
            'pusher': 'test-user',
            'commits': [{"test_commit": "hej"}],
            'timestamp': '2017-02-02T15:25:43.511Z'
        }

        model = RepositoryModel(external_id='test',
                                short_name="hello",
                                last_pusher='old-user',
                                head_sha='123',
                                previous_head_sha='234',
                                last_update='2017-02-02T12:25:43.511Z',
                                commits=[{"test_commit2": "hej"}])
        apply_events(RepositoryProjection.apply_event_to_model,
                     model,
                     [event1])

        assert model.external_id == 'test'
        assert model.short_name == 'test-repo'
        assert model.full_name == 'test-org/test-repo'
        assert model.type == 'GITHUB_ENTERPRISE'
        assert model.head_sha == '2'
        assert model.previous_head_sha == '1'
        assert len(model.commits) == 2
        assert model.last_pusher == 'test-user'
        assert model.last_update == dateutil.parser.parse('2017-02-02T15:25:43.511Z')

    def test_doesnt_apply_duplicate_commits(self):
        event1 = Container()
        event1.type = 'CodePushed'
        event1.body = {
            'identifier': {
                'shortName': 'test-repo',
                'fullName': 'test-org/test-repo',
                'repoType': 'GITHUB_ENTERPRISE'
            },
            'newHeadSha': '2',
            'previousHeadSha': '1',
            'pusher': 'test-user',
            'commits': [{"test_commit": "hej"}],
            'timestamp': '2017-02-02T15:25:43.511Z'
        }

        model = RepositoryModel(external_id='test',
                                short_name="hello",
                                last_pusher='old-user',
                                head_sha='123',
                                previous_head_sha='234',
                                last_update='2017-02-02T12:25:43.511Z',
                                commits=[{"test_commit": "hej"}])
        apply_events(RepositoryProjection.apply_event_to_model,
                     model,
                     [event1])

        assert len(model.commits) == 1

    def doesnt_apply_unrelated_event(self):
        event = Container()
        event.type = 'PipelineStarted'
        event.body = {
            'timestamp': '2017-02-02T14:25:43.511Z'
        }

        model = RepositoryModel(external_id='test',
                                short_name="hello",
                                full_name='test-org/hello',
                                last_pusher='old-user',
                                head_sha='123',
                                previous_head_sha='234',
                                last_update='2017-02-02T12:25:43.511Z',
                                commits=[{"test_commit": "hej"}])
        apply_events(RepositoryProjection.apply_event_to_model,
                     model,
                     [event])

        assert model.external_id == 'test'
        assert model.short_name == 'hello'
        assert model.full_name == 'test-org/hello'
        assert last_pusher == 'old-user'
