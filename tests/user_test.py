import json
from . import app, client, cache, create_token_internal, create_token_noninternal, init_database

class TestUserCrud():
    def test_user_list_internal(self, client, init_database):
        token = create_token_internal()
        data = {
            'sex':'male',
            'orderby':'age',
            'sort':'desc'
        }
        res = client.get('/user',
                        query_string=data,
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 200

    def test_user_list2_internal(self, client, init_database):
        token = create_token_internal()
        data = {
            'sex':'male',
            'orderby':'age',
            'sort':'asc'
        }
        res = client.get('/user',
                        query_string=data,
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 200

    def test_user_list3_internal(self, client, init_database):
        token = create_token_internal()
        data = {
            'sex':'male',
            'orderby':'sex',
            'sort':'desc'
        }
        res = client.get('/user',
                        query_string=data,
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 200

    def test_user_list4_internal(self, client, init_database):
        token = create_token_internal()
        data = {
            'sex':'male',
            'orderby':'sex',
            'sort':'asc'
        }
        res = client.get('/user',
                        query_string=data,
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 200

    def test_user_noninternal_list(self, client, init_database):
        token = create_token_noninternal()
        res = client.get('/user',
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 200


    def test_user_getid_internal(self, client, init_database):
        token = create_token_internal()
        res = client.get('/user/1',
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 200

    def test_user_getid_invalid_internal(self, client, init_database):
        token = create_token_internal()
        res = client.get('/user/100',
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 404

    
    def test_user_post_internal(self, client, init_database):
        token = create_token_internal()
        data = {
            'name':'Rahman',
            'age':24,
            'sex':'Male',
            'client_id': 2
        }
        res = client.post('/user',
                        data=json.dumps(data),
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 200

    
    def test_user_put_internal(self, client, init_database):
        token = create_token_internal()
        data = {
            'name':'Rahman',
            'age':24,
            'sex':'Male',
            'client_id': 2
        }
        res = client.put('/user/1',
                        data=json.dumps(data),
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 200


    def test_user_put_invalid_internal(self, client, init_database):
        token = create_token_internal()
        data = {
            'name':'Rahman',
            'age':24,
            'sex':'Male',
            'client_id': 2
        }
        res = client.put('/user/100',
                        data=json.dumps(data),
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 404

    
    def test_user_del_internal(self, client, init_database):
        token = create_token_internal()
        res = client.delete('/user/1',
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 200

    def test_user_del_invalid_internal(self, client, init_database):
        token = create_token_internal()
        res = client.delete('/user/100',
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 404