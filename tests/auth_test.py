import json
from . import app, client, cache, create_token_internal, create_token_noninternal, init_database

class TestTokenCrud():
    def test_token_get_internal(self, client, init_database):
        token = create_token_internal()
        data = {
            'client_key': 'qwe',
            'client_secret': 'rty'
        }
        res = client.get('/auth',
                        query_string=data,
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        assert res.status_code == 404

    def test_token_internal(self, client, init_database):
        token = create_token_internal()
        data = {
            'client_key': 'altarest',
            'client_secret': '12345'
        }
        res = client.post('/auth/refresh',
                        query_string=data,
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        assert res.status_code == 200