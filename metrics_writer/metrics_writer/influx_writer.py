def get_writing_method(clz_name):
    if clz_name == 'PipelineFinished':
        return write_pipeline_finished

    if clz_name == 'PipelineStageFinished':
        return write_pipeline_stage_finished

    if clz_name == 'CodePushed':
        return write_code_pushed

def write_pipeline_finished(influxdb_connection, event):
    data = [{
        "measurement": "pipeline.finished",
        "time": event.timestamp.ToNanoseconds(),
        "tags": {
            "pipeline_id": event.uuid,
            "result": event.result
        },
        "fields": {
                "duration": event.duration_ms
            }
        }]
    influxdb_connection.write_points(data)

def write_pipeline_stage_finished(influxdb_connection, event):
    data = [{
        "measurement": "pipeline.stage.finished",
        "time": event.timestamp.ToNanoseconds(),
        "tags": {
            "pipeline_id": event.pipeline_uuid,
            "stage_id": event.uuid,
            "result": event.result
        },
        "fields": {
                "duration": event.duration_ms
            }
        }]
    influxdb_connection.write_points(data)

def write_code_pushed(influxdb_connection, event):
    data = [{
        "measurement": "code.pushed",
        "time": event.timestamp.ToNanoseconds(),
        "tags": {
            "repository_name": event.repository_name,
            "user_id": event.pusher.id,
            "username": event.pusher.username
        },
        "fields": {
                "num_commits": len(event.commits)
            }
        }]
    influxdb_connection.write_points(data)
