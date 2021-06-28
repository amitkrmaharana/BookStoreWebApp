from flask import url_for


def test_register_user(client):
    """
    This method test the registration of a user
    :param client: application test client
    :return: Boolean
    """
    data = {
        "username": "test",
        "password": "test",
        "mobilenum": "9652262358",
        "email": "test@gmail.com"
    }
    response = client.post(url_for('book_store.register_user'), json=data)
    assert response.status_code == 200


def test_login_user(client):
    """
     Tests the login of a user
    :param client: application test client
    :return: Boolean
    """
    data = {
        "username": "test",
        "password": "test"
    }
    response = client.post(url_for('book_store.login_user'), json=data)
    assert response.status_code == 200


def test_add_books_to_the_database(client):
    """
    Tests if the books are added to the database or not
    :param client: application test client
    :return: checks status code and returns boolean
    """
    data = [
        {
            "author": "Ruby",
            "title": "Market",
            "quantity": 32,
            "price": 119,
            "description": "Shares the experience of the market"
        },
        {
            "author": "Ragini Bose",
            "title": "A ping",
            "quantity": 61,
            "price": 179,
            "description": "It's all about a ping"
        }
    ]
    response = client.post(url_for('book_store.add_books'), json=data)
    assert response.status_code == 200


def test_add_books_to_cart(client):
    """
    This method checks if the books are added to the cart or not
    :param client: application test client
    :return: url status code
    """
    token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoyfQ.VMA9aviYBT1KPxVlaqqbsHDkmbySq3cfIPITTATtR7U'
    data = {
        "book_id": 2,
        "quantity": 1
    }
    response = client.post(url_for('book_store.add_books_to_cart'), json=data, headers={"token": token})
    assert response.status_code == 200


def test_place_order(client):
    """
    This method tests if the order is placed or not
    :param client: application test client
    :return: url status code
    """
    token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoyfQ.VMA9aviYBT1KPxVlaqqbsHDkmbySq3cfIPITTATtR7U'
    response = client.post(url_for('book_store.place_order'), headers={"token": token})
    assert response.status_code == 200


def test_add_books_to_wishlist(client):
    """
    This method tests if the book is added to the wishlist
    :param client: application test client
    :return: url status code
    """
    token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoyfQ.VMA9aviYBT1KPxVlaqqbsHDkmbySq3cfIPITTATtR7U'
    data = {
        "book_id": 3
    }
    response = client.post(url_for('book_store.add_to_wishlist'), json=data, headers={"token": token})
    assert response.status_code == 200


def test_confirmation_mail(client):
    """
    This method tests sending of mail to the user
    :param client: application test client
    :return: status code
    """
    token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoyfQ.VMA9aviYBT1KPxVlaqqbsHDkmbySq3cfIPITTATtR7U'
    response = client.post(url_for('book_store.confirmation_mail'), headers={"token": token})
    assert response.status_code == 200


def test_delivery_trigger(client):
    """
    This method tests delivery is updated to true
    :param client: application test client
    :return: status code
    """
    data = {
        "order_id": 8
    }
    response = client.post(url_for('book_store.is_delivered'), json=data)
    assert response.status_code == 200
