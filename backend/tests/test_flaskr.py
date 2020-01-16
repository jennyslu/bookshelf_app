import json
import os
import unittest

from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from flaskr.models import setup_db, Book

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


def test_config():
    # make sure passing test config works as expected
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


def test_hello(client):
    response = client.get('/hello')
    assert response.get_json() == {'message': 'Hello, World!'}


class TestGetSpecificBook(object):

    def test_get_book_success(self, client):
        response = client.get('/books/4').get_json()
        assert response["success"]
        assert response['book'] == {'id': 4,
                                    'title': 'Educated: A Memoir',
                                    'author': 'Tara Westover',
                                    'rating': 5}

    def test_get_book_failure(self, client):
        response = client.get('books/400').get_json()
        assert not response["success"]
        assert response["error"] == 404


class TestAddBook(object):

    def test_add_book_success(self, client):
        response = client.post('/books', json={'title': 'Bible',
                                               'author': 'God',
                                               'rating': 1}).get_json()
        assert response["success"]

    def test_add_book_failure(self, client):
        response = client.post('/books', json={'random': 123}).get_json()
        assert not response["success"]
        assert response["error"] == 400


class TestSearchBook(object):

    def test_search_book_success(self, client):
        response = client.post('/books', json={'search': 'NOVEL'}).get_json()
        assert response["success"]
        assert response["total_books"] == 4
