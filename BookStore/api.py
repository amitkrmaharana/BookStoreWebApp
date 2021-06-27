import json

import jwt
from flask import Blueprint, request, make_response, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect

from BookStore.config import Config

book_store = Blueprint('book_store', __name__)
from BookStore.models import *


@book_store.route('/register', methods=['POST', 'GET'])
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
        return make_response(jsonify("Token not available"), 401)
