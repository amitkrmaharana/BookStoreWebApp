import json
import smtplib
import ssl
from functools import wraps

import jwt
from flask import Blueprint, request, make_response, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect

from BookStore.config import Config

book_store = Blueprint('book_store', __name__)
from BookStore.models import *


def verify_token(function):
    @wraps(function)
    def wrapper():
        if 'token' not in request.headers:
            resp = jsonify({'message': 'Token not provided in the header, Login is Required'})
            resp.status_code = 400
            logger.info('Token not provided in the header')
            return resp
        else:
            data_decode = jwt.decode(request.headers.get('token'), Config.SECRET_KEY, algorithms="HS256")

            return function(data_decode.get('user_id'))

    return wrapper


@book_store.route('/register', methods=['POST'])
def register_user():
    """
    This method registers a new user to the database
    :return: a new registration
    """
    try:
        if request.method == 'POST':
            data = request.json
            user = Users(username=data.get('username'),
                         mobilenum=data.get('mobilenum'),
                         password=generate_password_hash(data.get('password')),
                         email=data.get('email')
                         )
            db.session.add(user)
            db.session.commit()
            username = data.get('username')
            user = Users.query.filter(Users.username == username).first()
            if not user:
                return jsonify(message="Username not registered", success=False)
            else:
                token = jwt.encode({'user_id': user.id}, Config.SECRET_KEY)
                verify = redirect(url_for('book_store.is_verify', token=token, user_id=user.id))
                if verify:
                    return jsonify(message="Registration successful",
                                   success=True,
                                   data={"user_id": user.id, "username": user.username})
                return jsonify(message="Registration unsuccessful", success=False)
        else:
            return jsonify(message="Registration unsuccessful, did not hit POST method", success=False)
    except Exception as e:
        logger.exception(e)
        return jsonify(message="Request Invalid")


@book_store.route('/login', methods=['POST'])
def login_user():
    """
    This method makes a login if a valid username or password is provided
    :return: returns successful if logged in and unsuccessful if not logged in
    """
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')

        user = Users.query.filter(Users.username == username).first()
        if not user or not check_password_hash(user.password, password):
            return jsonify(message="Bad username or password", success=False)
        else:
            token = jwt.encode({'user_id': user.id}, Config.SECRET_KEY)
            verify = redirect(url_for('book_store.is_verify', token=token, user_id=user.id))
            if verify:
                return jsonify(message="Login Successful", success=True,
                               data={"username": username, "token": token})
            return jsonify(message="Login unsuccessful", success=False)

    except Exception as e:
        logger.exception(e)
        return jsonify(message="Bad request")


@book_store.route('/verify/<token>/<user_id>', methods=['GET'])
def is_verify(token=None, user_id=None):
    """
    This route decodes a given token and checks if the token is valid for a username or not
    :param user_id:
    :param token: token generated
    :return: boolean
    """
    try:
        data = jwt.decode(token, Config.SECRET_KEY, algorithms="HS256")
        if data.get('user_id') == user_id:
            return True
        return False
    except Exception as e:
        logger.exception(e)
        return jsonify(message="Token not available", success=False)


@book_store.route('/addbooks', methods=['POST'])
def add_books():
    """
    This method adds the book details to the database. This can only be done by admin
    :return: adds the book details to the database
    """
    try:
        if request.method == 'POST':
            book_data = request.json
            for book in book_data:
                details = Books(author=book.get('author'), title=book.get('title'),
                                quantity=book.get('quantity'), price=book.get('price'),
                                description=book.get('description'))
                db.session.add(details)
                db.session.commit()
            books = Books.query.all()
            data = json.dumps(Books.serialize_list(books))
            return jsonify(message="Books added", success=True,
                           data={"Books Added": data})
    except Exception as e:
        logger.exception(e)
        return jsonify(message='Bad request or books not added')


@book_store.route('/get_books', methods=['GET'])
@book_store.route('/get_books/<int:page>', methods=['GET'])
def get_books(page=1):
    """
    This method queries all the book details in Books database
    :return: book details in database , per page only 2 data are returned
    """
    try:
        books = Books.query.paginate(page, per_page=Config.BOOKS_PER_PAGE)
        data = json.dumps(Books.serialize_list(books.items))
        return jsonify(success=True, data={"Books": data})
    except Exception as e:
        logger.exception(e)
        return jsonify(message="404 Error", success=False)


@book_store.route('/search', methods=['POST'])
def search_books():
    """
    This method returns the books with a specific name or author name
    json contains the value of keyword
    :return: list of books
    """
    try:
        if request.method == 'POST':
            name = request.json
            books = Books.query.filter(
                (Books.title == name.get('keyword')) | (Books.author == name.get('keyword'))).all()
            data = json.dumps(Books.serialize_list(books))
            return jsonify(success=True,
                           data={"Book": data})
    except Exception as e:
        logger.exception(e)
        return jsonify(message='Bad request method')


@book_store.route('/cart', methods=['POST'])
@verify_token
def add_books_to_cart(user_id):
    """
    This method requires book id to add to the cart one by one
    json contains book id, quantity
    :param user_id: payload in the jwt
    :return:books id
    """
    try:
        if request.method == 'POST':
            data = request.json
            book = Books.query.filter(Books.id == data.get('book_id')).first()
            if book.quantity > 0:
                cart = Cart(user_id=user_id, book_id=data.get('book_id'),
                            quantity=data.get('quantity'))
                db.session.add(cart)
                book.quantity = book.quantity - data.get('quantity')
                db.session.commit()
                return jsonify(message='Books added to the cart', success=True,
                               data={"Book Title": book.title, "Quantity": data.get('quantity'),
                                     "Price per book": book.price})
            else:
                return jsonify(message='Book not available', success=False, )
        return jsonify(message='Should be a POST command', success=False)
    except Exception as e:
        logger.exception(e)
        return jsonify(message='Bad request method')


@book_store.route('/order', methods=['POST'])
@verify_token
def place_order(user_id):
    """
    This api uses the cart table to confirm the order
    :param user_id: logged in user
    :return: total amount of the order
    """
    try:
        if request.method == 'POST':
            total_price = 0
            carts = Cart.query.filter(Cart.user_id == user_id).all()
            for cart in carts:
                book = Books.query.filter(Books.id == cart.book_id).first()
                price = book.price * cart.quantity
                total_price = total_price + price
                db.session.delete(cart)
                orderbook = Orderbook(user_id=user_id, book_id=cart.book_id)
                db.session.add(orderbook)
                db.session.commit()
            order = Order(user_id=user_id, total_amount=total_price)
            db.session.add(order)
            db.session.commit()
            return jsonify(message='Order Placed', success=True,
                           data={"User id": user_id, "Total amount": total_price})
        return jsonify(message='Order Unsuccessful', success=False)
    except Exception as e:
        logger.exception(e)
        return jsonify(message='Bad request method')


@book_store.route('/wishlist', methods=['POST', 'GET'])
@verify_token
def add_to_wishlist(user_id):
    """
    Adds books to the wishlist of the user which is logged in
    :param user_id: logged in user
    :return: books added to wishlist table
    """
    try:
        if request.method == 'POST':
            data = request.json
            wishlist = Wishlist(user_id=user_id, book_id=data.get('book_id'))
            db.session.add(wishlist)
            db.session.commit()
            return jsonify(message='Books added to wishlist', success=True, data={"Book id": data.get('book_id')})
        return jsonify(message='Books not added to wishlist', success=False)
    except Exception as e:
        logger.exception(e)
        return jsonify(message='Bad request method')


@book_store.route('/send_mail', methods=['POST', 'GET'])
@verify_token
def confirmation_mail(user_id):
    """
    This method sends mail to the user upon confirmation of order
    :param user_id:
    :return:
    """
    try:
        user = Users.query.filter(Users.id == user_id).first()
        order = Order.query.filter(Order.user_id == user_id).first()
        port = 465
        password = Config.password
        sender = 'for657development@gmail.com'
        receiver = user.email
        message = """
Subject: Book order details
Your total amount for the 
books ordered is Rs.%d
""" % order.total_amount
        # Create a secure SSL context
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver, message)
            return jsonify(message='Mail sent to the %s' % user.username, success=True)
    except Exception as e:
        logger.exception(e)
        return jsonify(message='Bad request method')
