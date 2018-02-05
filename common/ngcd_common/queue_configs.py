from ngcd_common import events_pb2

HEADER_CLASS_MAP = {
    'PipelineStarted': events_pb2.PipelineStarted,
    'PipelineFinished': events_pb2.PipelineFinished,
    'PipelineStageStarted': events_pb2.PipelineStageStarted,
    'PipelineStageFinished': events_pb2.PipelineStageFinished,
    'CodePushed': events_pb2.CodePushed
}

def handle_headers(headers_map):
    if not headers_map:
        return None
    header_indicator = headers_map.get('proto-message-type', None)
    if not header_indicator:
        return None
    expected_clz = HEADER_CLASS_MAP.get(header_indicator, None)
    return expected_clz
