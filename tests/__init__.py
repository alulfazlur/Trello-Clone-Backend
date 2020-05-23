import pytest, json, logging, uuid, hashlib
from flask import Flask, request

from blueprints import app, db
from app import cache

from blueprints.book.model import Books
from blueprints.client.model import Clients
from blueprints.rent.model import Rent
from blueprints.user.model import Users

def call_client(request):
    client = app.test_client()
    return client

@pytest.fixture
def client(request):
    return call_client(request)

@pytest.fixture
def init_database():
    db.drop_all()
    db.create_all()

    salt = uuid.uuid4().hex
    encoded = ('%s%s' % ('12345', salt)).encode('utf-8')
    hash_pass = hashlib.sha512(encoded).hexdigest()
    client_int = Clients(client_key= "altarest", client_secret=hash_pass, status="True", salt=salt)
    client_noint = Clients(client_key= "alul", client_secret=hash_pass, status="False", salt=salt)
    db.session.add(client_int)
    db.session.add(client_noint)
    db.session.commit()

    book = Books(title='Judul Buku', isbn="123-456-789", writer="Alul")
    db.session.add(book)
    db.session.commit()

    user = Users (name='Alul', age=23 , sex='Male' , client_id=1 )
    db.session.add(user)
    db.session.commit()

    rent = Rent(book_id=1, user_id=1)
    db.session.add(rent)
    db.session.commit()

    yield db
    db.drop_all()

def create_token_internal():
    token = cache.get('test-token')
    if token is None:
        data = {
            'client_key': 'altarest',
            'client_secret': '12345'
        }
        req = call_client(request)
        res = req.get('/auth', query_string=data)
        
        res_json = json.loads(res.data)

        logging.warning('RESULT : %s', res_json)

        assert res.status_code == 200

        cache.set('test-token', res_json['token'], timeout=60)

        return res_json['token']
    else:
        return token


def create_token_noninternal():
    token = cache.get('test-token')
    if token is None:
        data = {
            'client_key': 'alul',
            'client_secret': '12345'
        }
        req = call_client(request)
        res = req.get('/auth', query_string=data)
        
        res_json = json.loads(res.data)

        logging.warning('RESULT : %s', res_json)

        assert res.status_code == 403

        cache.set('test-token', res_json['token'], timeout=60)

        return res_json['token']
    else:
        return token

