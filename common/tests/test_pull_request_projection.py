from ngcd_common.projections.projections import PullRequestProjection
from ngcd_common.model import PullRequest as PullRequestModel
import dateutil.parser

class Container(object):
    pass

def apply_events(func, model, events):
    for event in events:
        func(model, event)

class TestPullRequestProjection(object):
    def test_apply_single_created_event_to_empty(self):
        event = Container()
        event.type = 'PullRequestOpened'
        event.body = {
            'prRepo': {
                'shortName': 'test-repo',
                'fullName': 'test-org/test-repo',
                'repoType': 'GITHUB_ENTERPRISE'
            },
            'id': '1',
            'headSha': '23456',
            'baseSha': '12345',
            'branch': 'feature/my-feature',
            'baseRepo': {
                'shortName': 'test-repo',
                'fullName': 'test-org/test-repo',
                'repoType': 'GITHUB_ENTERPRISE'
            },
            'htmlUrl': 'http://someurl',
            'apiUrl': 'http://apiurl',
            'openedBy': {
                'id': '1',
                'userName': 'test-user',
                'email': 'test-email'
            },
            'timestamp': '2017-02-02T14:25:43.511Z'
        }
        model = PullRequestModel(external_id='test-org/test-repo/1')
        projection = PullRequestProjection()
        apply_events(projection.apply_event_to_model,
                     model,
                     [event])

        assert model.external_id == 'test-org/test-repo/1'
        assert model.is_closed == False
        assert model.repo_external_id == 'test-org/test-repo'
        assert model.head_sha == '23456'
        assert model.base_sha == '12345'
        assert model.branch == 'feature/my-feature'
        assert model.base_repo_external_id == 'test-org/test-repo'
        assert model.html_url == 'http://someurl'
        assert model.api_url == 'http://apiurl'
        assert model.opened_by == {
            'id': '1',
            'userName': 'test-user',
            'email': 'test-email'
        }
        assert model.closed_by == None
        assert model.opened_at == dateutil.parser.parse('2017-02-02T14:25:43.511Z')
        assert model.closed_at == None
        assert model.last_update == dateutil.parser.parse('2017-02-02T14:25:43.511Z')

    def test_open_then_close(self):
        event = Container()
        event.type = 'PullRequestOpened'
        event.body = {
            'prRepo': {
                'shortName': 'test-repo',
                'fullName': 'test-org/test-repo',
                'repoType': 'GITHUB_ENTERPRISE'
            },
            'id': '1',
            'headSha': '23456',
            'baseSha': '12345',
            'branch': 'feature/my-feature',
            'baseRepo': {
                'shortName': 'test-repo',
                'fullName': 'test-org/test-repo',
                'repoType': 'GITHUB_ENTERPRISE'
            },
            'htmlUrl': 'http://someurl',
            'apiUrl': 'http://apiurl',
            'openedBy': {
                'id': '1',
                'userName': 'test-user',
                'email': 'test-email'
            },
            'timestamp': '2017-02-02T14:25:43.511Z'
        }

        event2 = Container()
        event2.type = 'PullRequestClosed'
        event2.body = {
            'prRepo': {
                'shortName': 'test-repo',
                'fullName': 'test-org/test-repo',
                'repoType': 'GITHUB_ENTERPRISE'
            },
            'id': '1',
            'closedBy': {
                'id': '2',
                'userName': 'other-user',
                'email': 'other-email'
            },
            'timestamp': '2017-02-02T15:25:43.511Z'
        }
        model = PullRequestModel(external_id='test-org/test-repo/1')
        projection = PullRequestProjection()
        apply_events(projection.apply_event_to_model,
                     model,
                     [event, event2])

        assert model.external_id == 'test-org/test-repo/1'
        assert model.is_closed == True
        assert model.repo_external_id == 'test-org/test-repo'
        assert model.head_sha == '23456'
        assert model.base_sha == '12345'
        assert model.branch == 'feature/my-feature'
        assert model.base_repo_external_id == 'test-org/test-repo'
        assert model.html_url == 'http://someurl'
        assert model.api_url == 'http://apiurl'
        assert model.opened_by == {
            'id': '1',
            'userName': 'test-user',
            'email': 'test-email'
        }
        assert model.closed_by == {
            'id': '2',
            'userName': 'other-user',
            'email': 'other-email'
        }
        assert model.opened_at == dateutil.parser.parse('2017-02-02T14:25:43.511Z')
        assert model.closed_at == dateutil.parser.parse('2017-02-02T15:25:43.511Z')
        assert model.last_update == dateutil.parser.parse('2017-02-02T15:25:43.511Z')
