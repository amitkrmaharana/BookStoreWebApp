from flask import url_for


def test_register_user(client):
    data = {
        "username": "test",
        "password": "test",
        "mobilenum": "9652262358",
        "email": "test@gmail.com"
    }
    response = client.post(url_for('book_store.register_user'), json=data)
    assert response.status_code == 200


def test_login_user(client):
    data = {
        "username": "test",
        "password": "test"
    }
    response = client.post(url_for('book_store.login_user'), json=data)
    assert response.status_code == 200
