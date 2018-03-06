NGCD
----
This project is a prototype to explore event-driven Continuous delivery.
The aim is to build a platform that can receive events from other systems, such as Jenkins or Github/Gitlab/BitBucket etc.

It's driven by RabbitMQ and Python. It makes use of the excellent Kombu framework for interacting with RabbitMQ, SQLAlchemy for database management and Flask for all APIs.

Components
----------
The system consists of the following components:
- _common_: Python+Protobuf. Defines the common Python package, including protobuf declarations, queue-configurations and data model. It also contains projections for replaying events into the data models.

- _event-api_: Python. Replays events and projects them to a backing data store, also exposes that data through a REST-api.

- _event-writer_: Python. Listens to events on the event bus and writes them into the event store.

- _metrics-writer_: Python. Experimental module that listens to events and writes them to InfluxDB for metrics-analysis.

- _ngcd-ui_: React+Redux. The UI that talks to the event_api and displays information about pipelines etc. It's based on [react-boilerplate](https://github.com/react-boilerplate/react-boilerplate/)

- _publisher_: Python. Generates input-events to the system. Has a generic REST-component as well as a component that understands GitLab webhooks and translates them to the internal Protobuf format.

- _validator_: Python. Acts as a gateway between external events (from the publisher) and forwards them to the internal queues (consumed by event_writer, metrics_writer and any other system one would like)
