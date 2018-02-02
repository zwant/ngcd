.PHONY: proto clean

proto:
	protoc -I=./common/proto --python_out=./common/ngcd_common ./common/proto/*.proto

clean:
	rm -f ./common/ngcd_common/events_pb2.py*

run-validator:
	source env/bin/activate; cd validator; python validator/run.py

run-publisher:
	source env/bin/activate; cd publisher; FLASK_APP="publisher.app" FLASK_DEBUG=true flask run

run-event-writer:
	source env/bin/activate; cd event_writer; python -m event_writer

run-event-api:
	source env/bin/activate; cd event_api; FLASK_APP="event_api.app" FLASK_DEBUG=true flask run -p 5001 --reload

create-events:
	curl -s --output /dev/null http://localhost:5000/pipeline_started/svante; \
	curl -s --output /dev/null http://localhost:5000/pipeline_finished/svante; \
	curl -s --output /dev/null http://localhost:5000/pipeline_stage_started/stage1/svante; \
	curl -s --output /dev/null http://localhost:5000/pipeline_stage_finished/stage1/svante; \
	curl -s --output /dev/null http://localhost:5000/pipeline_started/other; \
	curl -s --output /dev/null http://localhost:5000/pipeline_stage_started/stage1/other; \
	curl -s --output /dev/null http://localhost:5000/pipeline_stage_finished/stage1/other; \
	curl -s --output /dev/null http://localhost:5000/pipeline_stage_started/stage2/other; \
	curl -s --output /dev/null -H "Content-Type: application/json" -X POST -d \
	'{"new_head_sha": "23456","previous_head_sha": "00000","user": {"id": "1","username": "svante","email": "svante@paldan.se"},"commits": [{"sha": "12345","message": "test commit!"},{"sha": "23456","message": "test commit number 2!"}]}' \
	http://localhost:5000/push/testrepo/23456

install-common-deps:
	source env/bin/activate; cd common; pip install --editable .

install-validator-deps:
	source env/bin/activate; cd validator; pip install --editable .

install-publisher-deps:
	source env/bin/activate; cd publisher; pip install --editable .

install-event-writer-deps:
	source env/bin/activate; cd event_writer; pip install --editable .

install-event-api-deps:
	source env/bin/activate; cd event_api; pip install --editable .

install-deps: install-common-deps install-validator-deps install-publisher-deps install-event-writer-deps install-event-api-deps

create-venv:
	python3 -m venv env
