from ngcd_common import events_pb2
from kombu import Exchange, Queue

EXTERNAL_EXCHANGE = Exchange('external', 'topic', durable=True)
INTERNAL_EXCHANGE = Exchange('internal', 'topic', durable=True)

HEADER_CLASS_MAP = {
    'PipelineStarted': events_pb2.PipelineStarted,
    'PipelineFinished': events_pb2.PipelineFinished,
    'PipelineStageStarted': events_pb2.PipelineStageStarted,
    'PipelineStageFinished': events_pb2.PipelineStageFinished,
    'CodePushed': events_pb2.CodePushed,
    'ArtifactPublished': events_pb2.ArtifactPublished,
    'RepositoryAdded': events_pb2.RepositoryAdded,
    'RepositoryRemoved': events_pb2.RepositoryRemoved
}

EXTERNAL_QUEUES = {
    'pipeline.started': Queue('external.pipeline.started', exchange=EXTERNAL_EXCHANGE, routing_key='pipeline.started'),
    'pipeline.finished': Queue('external.pipeline.finished', exchange=EXTERNAL_EXCHANGE, routing_key='pipeline.finished'),
    'pipeline.stage.started': Queue('external.pipeline.stage.started', exchange=EXTERNAL_EXCHANGE, routing_key='pipeline.stage.started'),
    'pipeline.stage.finished': Queue('external.pipeline.stage.finished', exchange=EXTERNAL_EXCHANGE, routing_key='pipeline.stage.finished'),
    'scm.repo.push': Queue('external.scm.repo.push', exchange=EXTERNAL_EXCHANGE, routing_key='scm.repo.push'),
    'scm.repo.create': Queue('external.scm.repo.create', exchange=EXTERNAL_EXCHANGE, routing_key='scm.repo.create'),
    'scm.repo.remove': Queue('external.scm.repo.remove', exchange=EXTERNAL_EXCHANGE, routing_key='scm.repo.remove'),
    'scm.artifact.publish': Queue('external.scm.artifact.publish', exchange=EXTERNAL_EXCHANGE, routing_key='artifact.publish')
}

INTERNAL_QUEUES = {
    'pipeline.started': Queue('internal.pipeline.started', exchange=INTERNAL_EXCHANGE, routing_key='pipeline.started'),
    'pipeline.finished': Queue('internal.pipeline.finished', exchange=INTERNAL_EXCHANGE, routing_key='pipeline.finished'),
    'pipeline.stage.started': Queue('internal.pipeline.stage.started', exchange=INTERNAL_EXCHANGE, routing_key='pipeline.stage.started'),
    'pipeline.stage.finished': Queue('internal.pipeline.stage.finished', exchange=INTERNAL_EXCHANGE, routing_key='pipeline.stage.finished'),
    'scm.repo.push': Queue('internal.scm.repo.push', exchange=INTERNAL_EXCHANGE, routing_key='scm.repo.push'),
    'scm.repo.create': Queue('internal.scm.repo.create', exchange=INTERNAL_EXCHANGE, routing_key='scm.repo.create'),
    'scm.repo.remove': Queue('internal.scm.repo.remove', exchange=INTERNAL_EXCHANGE, routing_key='scm.repo.remove'),
    'scm.artifact.publish': Queue('internal.scm.artifact.publish', exchange=INTERNAL_EXCHANGE, routing_key='artifact.publish')
}

def handle_headers(headers_map):
    if not headers_map:
        return None
    header_indicator = headers_map.get('proto-message-type', None)
    if not header_indicator:
        return None
    expected_clz = HEADER_CLASS_MAP.get(header_indicator, None)
    return expected_clz
