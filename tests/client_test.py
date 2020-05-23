import json
from . import app, client, cache, create_token_internal, create_token_noninternal, init_database

class TestClientCrud():
    
    def test_client_list_internal(self, client, init_database):
        data = {
            'status':'true',
            'orderby':'id',
            'sort':'asc'
        }
        token = create_token_internal()
        res = client.get('/client',
                        query_string=data,
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 200

    def test_client_list2_internal(self, client, init_database):
        data = {
            'orderby':'id',
            'sort':'desc'
        }
        token = create_token_internal()
        res = client.get('/client',
                        query_string=data,
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 200

    def test_client_list3_internal(self, client, init_database):
        data = {
            'orderby':'status',
        }
        token = create_token_internal()
        res = client.get('/client',
                        query_string=data,
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 200


    def test_client_list_noninternal(self, client, init_database):
        token = create_token_noninternal()
        res = client.get('/client',
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 200


    def test_client_getid_internal(self, client, init_database):
        token = create_token_internal()
        res = client.get('/client/1',
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')
        res_json = json.loads(res.data)
        assert res.status_code == 200


    def test_client_getid_invalid_internal(self, client, init_database):
        token = create_token_internal()
        res = client.get('/client/100',
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 404


    def test_client_post_internal(self, client, init_database):
        token = create_token_internal()
        data = {
            'client_key':'fazlur',
            'client_secret':'1234',
            'status':'true'
        }
        res = client.post('/client',
                        data=json.dumps(data),
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 200


    def test_client_put_internal(self, client, init_database):
        token = create_token_internal()
        data = {
            'client_key':'lula',
            'client_secret':'1434',
            'status':'true'
        }
        res = client.put('/client/2',
                        data=json.dumps(data),
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 200


    def test_client_put_invalid_internal(self, client, init_database):
        token = create_token_internal()
        data = {
            'client_key':'lula',
            'client_secret':'1434',
            'status':'true'
        }
        res = client.put('/client/100',
                        data=json.dumps(data),
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 404


    def test_client_delete_internal(self, client, init_database):
        token = create_token_internal()
        res = client.delete('/client/2',
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 200
        

    def test_client_delete_invalid_internal(self, client, init_database):
        token = create_token_internal()
        res = client.delete('/client/100',
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 404