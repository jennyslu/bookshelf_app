import logging

from flask import Blueprint, abort, jsonify, request
from sqlalchemy import or_
from sqlalchemy.sql import func

from ..models import Book

bp = Blueprint('home', __name__)

BOOKS_PER_SHELF = 8


# CORS Headers
@bp.after_request
def after_request(response):
    # True to allow content-type authorization
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    # all methods we are intending to use
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


@bp.route('/')
def index():
    return jsonify({'message': 'HELLO WORLD'})


@bp.route('/hello')
def get_greeting():
    return jsonify({'message': 'Hello, World!'})


@bp.route('/books', methods=['GET'])
def get_books():
    # get value of page from request param arguments, default 1, type int
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * BOOKS_PER_SHELF
    end = start + BOOKS_PER_SHELF
    books = Book.query.order_by(Book.id).all()
    # even if index is out of range this list comp won't fail...
    formatted_books = [book.format() for book in books[start:end]]
    if len(formatted_books) == 0:
        abort(404)
    else:
        return jsonify({'success': True, 'books': formatted_books, 'total_books': len(books)})


@bp.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.get(book_id)
    if book is None:
        abort(404)
    book.delete()

    return jsonify({'success': True, 'deleted': book_id})


@bp.route('/books/<int:book_id>', methods=['PATCH'])
def update_book(book_id):
    request_data = request.get_json()
    book = Book.query.get(book_id)
    if book is None:
        abort(404)
    try:
        book.rating = request_data["rating"]
    except Exception:
        abort(400)
    book.update()

    return jsonify({'success': True, 'book': book.format()})


@bp.route('/books', methods=['POST'])
def add_book():
    request_data = request.get_json()
    # searching for a book
    if 'search' in request_data:
        sql_search = "%{}%".format(request_data["search"])
        # ilike is case-insensitive LIKE: lower(a) LIKE lower(other)
        books = Book.query.filter(or_(Book.title.ilike(sql_search),
                                      Book.author.ilike(sql_search))).order_by(Book.id).all()
        formatted_books = [book.format() for book in books]
        return jsonify({'success': True, 'total_books': len(books), 'books': formatted_books})
    # adding a book
    else:
        max_book_id = Book.query.order_by(Book.id.desc()).first().id
        request_data['id'] = max_book_id + 1
        try:
            book = Book(**request_data)
        except Exception as e:
            logging.critical('failed to add new book: %s', e, exc_info=True)
            abort(400)
        book.insert()

        return jsonify({
            'success': True,
            'book': book.format(),
        })


@bp.route('/books/<int:book_id>')
def get_specific_book(book_id):
    book = Book.query.get(book_id)
    if book is None:
        abort(404)
    else:
        return jsonify({'success': True, 'book': book.format()})


"""
when using the errorhandler decorator, take into account:
* passing the status code/Python error as an argument to the decorator
* logical naming of function handler
* consistent formatting and messaging of the JSON response object

NOW EVERYWHERE WE HAVE abort(404) THIS JSON MESSAGE WILL BE RETURNED INSTEAD
"""
@bp.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": 404, "message": "Resource not found"}), 404


@bp.errorhandler(422)
def unprocessable(error):
    return jsonify({"success": False, "error": 422, "message": "Unprocessable"}), 422


@bp.errorhandler(400)
def bad_request(error):
    return jsonify({"success": False, "error": 400, "message": "Bad request"}), 400


@bp.errorhandler(405)
def bad_method(error):
    return jsonify({"success": False, "error": 405, "message": "Method not allowed"})


"""
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy #, or_
from flask_cors import CORS
import random

from models import setup_db, Book

BOOKS_PER_SHELF = 8


def paginate_books(request, selection):
    page = request.args.get('page', 1, type=int)
    start =  (page - 1) * BOOKS_PER_SHELF
    end = start + BOOKS_PER_SHELF

    books = [book.format() for book in selection]
    current_books = books[start:end]

    return current_books

def create_app(test_config=None):
  # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

  # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response


    @app.route('/books')
    def retrieve_books():

        selection = Book.query.order_by(Book.id).all()
        current_books = paginate_books(request, selection)

        if len(current_books) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'books': current_books,
            'total_books': len(Book.query.all())
        })

    @app.route('/books/<int:book_id>', methods=['PATCH'])
    def update_book(book_id):

        body = request.get_json()

        try:
            book = Book.query.filter(Book.id == book_id).one_or_none()
            if book is None:
                abort(404)

            if 'rating' in body:
                book.rating = int(body.get('rating'))

                book.update()

                return jsonify({
                    'success': True,
                })

        except:
            abort(400)

    @app.route('/books/<int:book_id>', methods=['DELETE'])
    def delete_book(book_id):
        try:
            book = Book.query.filter(Book.id == book_id).one_or_none()

            if book is None:
                abort(404)

            book.delete()
            selection = Book.query.order_by(Book.id).all()
            current_books = paginate_books(request, selection)

            return jsonify({
                'success': True,
                'deleted': book_id,
                'books': current_books,
                'total_books': len(Book.query.all())
            })

        except:
            abort(422)

    @app.route('/books', methods=['POST'])
    def create_book():
        body = request.get_json()

        new_title = body.get('title', None)
        new_author = body.get('author', None)
        new_rating = body.get('rating', None)

        try:
            book = Book(title=new_title, author=new_author, rating=new_rating)
            book.insert()

            selection = Book.query.order_by(Book.id).all()
            current_books = paginate_books(request, selection)
            import pdb; pdb.set_trace()

            return jsonify({
                'success': True,
                'created': book.id,
                'books': current_books,
                'total_books': len(Book.query.all())
            })

        except:
            abort(422)

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    return app
"""
