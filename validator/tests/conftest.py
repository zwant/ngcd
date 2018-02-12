import os
import pytest
from kombu import Connection

AMQP_URL = 'memory:///'

@pytest.fixture(scope='function')
def amqp_connection(request):
    connection = Connection(AMQP_URL, transport_options={"polling_interval": 0})

    def teardown():
        connection.release()

    request.addfinalizer(teardown)
    return connection
