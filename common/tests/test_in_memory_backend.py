from ngcd_common.projections.projection_backends import InMemoryBackend
from ngcd_common.model import Pipeline, PipelineStage

class TestInMemoryBackend(object):
    def setup_method(self, method):
        self.backend = InMemoryBackend(empty=True)

    def test_save_one(self):
        model = Pipeline(id=1, external_id="1")
        self.backend.save(model)

        assert len(self.backend._get_data()) == 1
        assert 'pipelines' in self.backend._get_data()
        pipelines_stored = self.backend._get_data()['pipelines']
        assert len(pipelines_stored) == 1
        assert pipelines_stored[0].external_id == "1"

    def test_save_two(self):
        model = Pipeline(id=1, external_id="1")
        self.backend.save(model)
        model = Pipeline(id=2, external_id="2")
        self.backend.save(model)

        assert len(self.backend._get_data()) == 1
        assert 'pipelines' in self.backend._get_data()
        pipelines_stored = self.backend._get_data()['pipelines']
        assert len(pipelines_stored) == 2
        assert pipelines_stored[0].external_id == "1"
        assert pipelines_stored[1].external_id == "2"

    def test_get_by_external_id(self):
        model1 = Pipeline(id=1, external_id="1")
        self.backend.save(model1)
        model2 = Pipeline(id=2, external_id="2")
        self.backend.save(model2)
        model3 = PipelineStage(id=3, external_id="1", pipeline_id='1')
        self.backend.save(model3)

        pipeline1 = self.backend.get_one_by_external_id('1', Pipeline)
        assert pipeline1.external_id == model1.external_id

        pipeline2 = self.backend.get_one_by_external_id('2', Pipeline)
        assert pipeline2.external_id == model2.external_id

        pipeline_stage = self.backend.get_one_by_external_id('1', PipelineStage)
        assert pipeline_stage.external_id == model3.external_id

    def test_get_or_create_by_external_id(self):
        model1 = Pipeline(id=1, external_id="1")
        self.backend.save(model1)

        pipeline1 = self.backend.get_or_create_by_external_id('1', Pipeline)
        assert pipeline1 is not None
        assert pipeline1.external_id == '1'
        assert pipeline1.result is None

        pipeline2 = self.backend.get_or_create_by_external_id('2', Pipeline)
        assert pipeline2 is not None
        assert pipeline2.external_id == '2'
        assert pipeline2.result is None

    def test_get_one_by_filter(self):
        model1 = Pipeline(id=1, external_id="1", result='SUCCESS')
        self.backend.save(model1)
        model2 = Pipeline(id=2, external_id="1", result='FAILURE')
        self.backend.save(model2)
        model3 = PipelineStage(id=3, external_id="1", pipeline_id='1')
        self.backend.save(model3)

        pipeline1 = self.backend.get_one_by_filter(Pipeline, {'external_id': '1',
                                                          'result':'SUCCESS'})
        assert pipeline1.external_id == '1'
        assert pipeline1.result == 'SUCCESS'

    def test_get_all_by_filter(self):
        model1 = Pipeline(id=1, external_id="1", result='SUCCESS')
        self.backend.save(model1)
        model2 = Pipeline(id=2, external_id="2", result='SUCCESS')
        self.backend.save(model2)
        model3 = PipelineStage(id=3, external_id="1", pipeline_id='1')
        self.backend.save(model3)

        found_pipelines = self.backend.get_by_filter(Pipeline, {'result':'SUCCESS'})
        assert len(found_pipelines) == 2

    def test_get_or_create_by_filter(self):
        model1 = Pipeline(id=1, external_id="1", result='SUCCESS')
        self.backend.save(model1)
        model2 = Pipeline(id=2, external_id="1", result='FAILURE')
        self.backend.save(model2)
        model3 = PipelineStage(id=3, external_id="1", pipeline_id='1')
        self.backend.save(model3)

        pipeline1 = self.backend.get_or_create_by_filter('1', Pipeline, {'external_id': '1',
                                                                         'result':'SUCCESS'})
        assert pipeline1 == model1

        pipeline2 = self.backend.get_or_create_by_filter('2', Pipeline, {'external_id': '2',
                                                                         'result':'SUCCESS'})
        assert pipeline2 is not None
        assert pipeline2.external_id == '2'
        assert pipeline2.result is None
