import json
from . import app, client, cache, create_token_internal, create_token_noninternal, init_database

class TestRentCrud():
    def test_rent_list_internal(self, client, init_database):
        token = create_token_internal()
        data = {
            'p':1,
            'rp':5,
            'book_id':1,
            'user_id':1,
            'orderby':'book_id',
            'sort': 'desc'
        }
        res = client.get('/rent',
                        query_string=data,
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 200

    def test_rent_list2_internal(self, client, init_database):
        token = create_token_internal()
        data = {
            'p':1,
            'rp':5,
            'book_id':1,
            'user_id':1,
            'orderby':'book_id',
            'sort': 'asc'
        }
        res = client.get('/rent',
                        query_string=data,
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 200

    def test_rent_list3_internal(self, client, init_database):
        token = create_token_internal()
        data = {
            'p':1,
            'rp':5,
            'book_id':1,
            'user_id':1,
            'orderby':'user_id',
            'sort': 'desc'
        }
        res = client.get('/rent',
                        query_string=data,
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 200

    def test_rent_list4_internal(self, client, init_database):
        token = create_token_internal()
        data = {
            'p':1,
            'rp':5,
            'book_id':1,
            'user_id':1,
            'orderby':'user_id',
            'sort': 'asc'
        }
        res = client.get('/rent',
                        query_string=data,
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 200

    def test_rent_get_internal(self, client, init_database):
        token = create_token_internal()
        res = client.get('/rent/1',
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 200

    def test_rent_get_invalid_internal(self, client, init_database):
        token = create_token_internal()
        res = client.get('/rent/100',
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 404

    def test_rent_post_internal(self, client, init_database):
        data = {
            'book_id':1,
            'user_id':1
        }
        token = create_token_internal()
        res = client.post('/rent',
                        data=json.dumps(data),
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 200