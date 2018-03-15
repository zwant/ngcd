.PHONY: proto clean

proto:
	protoc -I=./common/proto --python_out=./common/ngcd_common ./common/proto/*.proto

clean:
	rm -f ./common/ngcd_common/events_pb2.py*

test-all:
	source env/bin/activate; pytest -v

# Running
run-validator:
	source env/bin/activate; cd validator; RABBITMQ_HOST='localhost' python validator/run.py

run-metrics-writer:
	source env/bin/activate; cd metrics_writer; python metrics_writer/run.py

run-publisher:
	source env/bin/activate; cd publisher; FLASK_APP="publisher.app" FLASK_DEBUG=true flask run -p 5000

run-event-writer:
	source env/bin/activate; cd event_writer; CLEAN_DB="true" python event_writer/run.py

run-event-api:
	source env/bin/activate; cd event_api; CLEAN_DB="true" FLASK_APP="event_api.app" FLASK_DEBUG=true flask run -p 5001 --reload

run-ui:
	cd ngcd_ui; npm run start

# Docker
build-validator-docker:
	docker build -t zwant/ngcd-validator:latest --build-arg APP_NAME=validator .

push-validator-dockerhub:
	docker push zwant/ngcd-validator:latest

build-event-writer-docker:
	docker build -t zwant/ngcd-event-writer:latest --build-arg APP_NAME=event_writer .

push-event-writer-dockerhub:
	docker push zwant/ngcd-event-writer:latest

build-event-api-docker:
	docker build -t zwant/ngcd-event-api:latest --build-arg APP_NAME=event_api .

push-event-api-dockerhub:
	docker push zwant/ngcd-event-api:latest

build-publisher-docker:
	docker build -t zwant/ngcd-publisher:latest --build-arg APP_NAME=publisher .

push-publisher-dockerhub:
	docker push zwant/ngcd-publisher:latest

build-ui-docker:
	docker build -t zwant/ngcd-ui:latest ./ngcd_ui

push-ui-dockerhub:
	docker push zwant/ngcd-ui:latest

build-docker: build-validator-docker build-event-api-docker build-event-writer-docker build-publisher-docker build-ui-docker

push-docker: push-validator-dockerhub push-event-writer-dockerhub push-event-api-dockerhub push-publisher-dockerhub push-ui-dockerhub

build-push-docker: build-docker push-docker

create-events:
	curl -s --output /dev/null -H "Content-Type: application/json" -X POST -d \
	'{"timestamp": "2012-04-23T18:25:43.511Z"}' http://localhost:5000/pipeline_started/svante/; \
	curl -s --output /dev/null -H "Content-Type: application/json" -X POST -d \
	'{"timestamp": "2012-04-23T18:25:43.511Z","duration_ms": 123456,"result": "SUCCESS"}' http://localhost:5000/pipeline_finished/svante/; \
	curl -s --output /dev/null -H "Content-Type: application/json" -X POST -d \
	'{"timestamp": "2012-04-23T18:25:43.511Z","pipeline_uuid": "svante"}' http://localhost:5000/pipeline_stage_started/stage1/; \
	curl -s --output /dev/null -H "Content-Type: application/json" -X POST -d \
	'{"timestamp": "2012-04-23T18:25:43.511Z","pipeline_uuid": "svante","duration_ms": 123456,"result": "SUCCESS"}' http://localhost:5000/pipeline_stage_finished/stage1/; \
	curl -s --output /dev/null -H "Content-Type: application/json" -X POST -d \
	'{"timestamp": "2012-04-23T18:25:43.511Z"}' http://localhost:5000/pipeline_started/other/; \
	curl -s --output /dev/null -H "Content-Type: application/json" -X POST -d \
	'{"timestamp": "2012-04-23T18:25:43.511Z","pipeline_uuid": "other"}' http://localhost:5000/pipeline_stage_started/stage1/; \
	curl -s --output /dev/null -H "Content-Type: application/json" -X POST -d \
	'{"timestamp": "2012-04-23T18:25:43.511Z","pipeline_uuid": "other","duration_ms": 123456,"result": "SUCCESS"}' http://localhost:5000/pipeline_stage_finished/stage1/; \
	curl -s --output /dev/null -H "Content-Type: application/json" -X POST -d \
	'{"timestamp": "2012-04-23T18:25:43.511Z","pipeline_uuid": "other"}' http://localhost:5000/pipeline_stage_started/stage2/; \
	curl -s --output /dev/null -H "Content-Type: application/json" -X POST -d \
	'{"timestamp": "2012-04-23T18:25:43.511Z", "new_head_sha": "23456","previous_head_sha": "00000","user": {"id": "1","username": "svante","email": "dummy@example.com"},"commits": [{"sha": "12345","message": "test commit!", "timestamp": "2012-04-23T18:25:43.511Z"},{"sha": "23456","message": "test commit number 2!", "timestamp": "2012-04-23T18:25:43.511Z"}]}' \
	http://localhost:5000/push/testrepo/23456/; \
	curl -s --output /dev/null -H "Content-Type: application/json" -X POST -d \
	'{"timestamp": "2012-04-23T18:25:43.511Z","new_head_sha": "34567","previous_head_sha": "23456","user": {"id": "1","username": "svante","email": "dummy@example.com"},"commits": [{"sha": "23456","message": "test commit!", "timestamp": "2012-04-23T18:25:43.511Z"},{"sha": "34567","message": "test commit number 2!", "timestamp": "2012-04-23T18:25:43.511Z"}]}' \
	http://localhost:5000/push/otherrepo/34567/

# Install deps
install-common-deps:
	source env/bin/activate; cd common; pip install -r requirements-test.txt

install-validator-deps:
	source env/bin/activate; cd validator; pip install -r requirements-test.txt

install-publisher-deps:
	source env/bin/activate; cd publisher; pip install -r requirements-test.txt

install-event-writer-deps:
	source env/bin/activate; cd event_writer; pip install -r requirements-test.txt

install-metrics-writer-deps:
	source env/bin/activate; cd metrics_writer; pip install -r requirements-test.txt

install-event-api-deps:
	source env/bin/activate; cd event_api; pip install -r requirements-test.txt

install-deps: install-common-deps install-validator-deps install-publisher-deps install-event-writer-deps install-event-api-deps

create-venv:
	python3 -m venv env

test: test-all
