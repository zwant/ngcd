import os
import pytest

from ngcd_common import model

SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres@localhost:5432/test_db'
CREATE_DB_URI = 'postgresql+psycopg2://postgres@localhost:5432/postgres'

@pytest.fixture(scope='session')
def db_engine(request):
    from sqlalchemy import create_engine
    import contextlib
    import sqlalchemy.exc

    with create_engine(
        CREATE_DB_URI,
        isolation_level='AUTOCOMMIT'
    ).connect() as connection:
        with contextlib.suppress(sqlalchemy.exc.ProgrammingError):
            connection.execute("create database test_db")

    _db_engine = create_engine(SQLALCHEMY_DATABASE_URI)

    def teardown():
        # We need to dispose of the connection pool, to allow ourselves to remove the db
        _db_engine.dispose()
        with create_engine(
            CREATE_DB_URI,
            isolation_level='AUTOCOMMIT'
        ).connect() as connection:
            connection.execute("drop database test_db")

    model.Base.metadata.create_all(_db_engine)

    request.addfinalizer(teardown)

    return _db_engine


@pytest.fixture(scope='function')
def session(db_engine, request):
    """Creates a new database session for a test."""
    from sqlalchemy.orm import scoped_session
    from sqlalchemy.orm import sessionmaker

    connection = db_engine.connect()
    transaction = connection.begin()

    session = scoped_session(sessionmaker(autocommit=False,
                                          autoflush=False,
                                          bind=connection))

    model.Base.query = session.query_property()

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)
    return session
