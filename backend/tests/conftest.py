import os

import pytest
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


@pytest.fixture(scope='session')
def app():
    app = create_app(test_config={
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'postgresql://jlu@localhost:5432/bookshelf_test',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    })
    # binds the app to the current context
    with app.app_context():
        db = SQLAlchemy(app)
        # create all tables
        db.create_all()
    db.engine.execute(_data_sql)

    yield app
    print('teardown')
    # for some reason this doesn't work - WHY????? db.drop_all()
    db.engine.execute('DROP TABLE books;')


@pytest.fixture(scope='session')
def client(app):
    return app.test_client()


@pytest.fixture(scope='session')
def runner(app):
    return app.test_cli_runner()
