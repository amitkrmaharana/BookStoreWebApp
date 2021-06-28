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
    token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoyfQ.VMA9aviYBT1KPxVlaqqbsHDkmbySq3cfIPITTATtR7U'
    data = {
        "book_id": 2,
        "quantity": 1
    }
    response = client.post(url_for('book_store.add_books_to_cart'), json=data, headers={"token": token})
    assert response.status_code == 200

