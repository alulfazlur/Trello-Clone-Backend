import json
from . import app, client, cache, create_token_internal, create_token_noninternal, init_database

class TestBookCrud():
    def test_book_list_internal(self, client, init_database):
        token = create_token_internal()
        data = {
            'title':'Judul Buku',
            'orderby':'title',
            'sort':'desc'
        }
        res = client.get('/book',
                        query_string=data,
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 200


    def test_book_list2_internal(self, client, init_database):
        token = create_token_internal()
        data = {
            'isbn':'123-456-789',
            'orderby':'title',
            'sort':'asc'
        }
        res = client.get('/book',
                        query_string=data,
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 200


    def test_book_list3_internal(self, client, init_database):
        token = create_token_internal()
        data = {
            'isbn':'123-456-789',
            'orderby':'isbn',
            'sort':'asc'
        }
        res = client.get('/book',
                        query_string=data,
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 200


    def test_book_list4_internal(self, client, init_database):
        token = create_token_internal()
        data = {
            'isbn':'123-456-789',
            'orderby':'isbn',
            'sort':'desc'
        }
        res = client.get('/book',
                        query_string=data,
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 200


    def test_book_list_noninternal(self, client, init_database):
        token = create_token_noninternal()
        res = client.get('/book',
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 200

    def test_book_get_internal(self, client, init_database):
        token = create_token_internal()
        res = client.get('/book/1',
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 200

    def test_book_get_invalid_internal(self, client, init_database):
        token = create_token_internal()
        res = client.get('/book/100',
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 404

    def test_book_post_internal(self, client, init_database):
        data = {
            'title':'Book Title',
            'isbn':'12345',
            'writer':'Fazlur'
        }
        token = create_token_internal()
        res = client.post('/book',
                        data=json.dumps(data),
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 200

    def test_book_put_internal(self, client, init_database):
        data = {
            'title':'BookTitle',
            'isbn':'1234567',
            'writer':'Rahman'
        }
        token = create_token_internal()
        res = client.put('/book/1',
                        data=json.dumps(data),
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 200


    def test_book_put_invalid_internal(self, client, init_database):
        data = {
            'title':'BookTitle',
            'isbn':'1234567',
            'writer':'Rahman'
        }
        token = create_token_internal()
        res = client.put('/book/100',
                        data=json.dumps(data),
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 404


    def test_book_del_internal(self, client, init_database):
        token = create_token_internal()
        res = client.delete('/book/1',
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 200

    def test_book_del_invalid_internal(self, client, init_database):
        token = create_token_internal()
        res = client.delete('/book/100',
                        headers={'Authorization':'Bearer ' + token},
                        content_type='application/json')

        res_json = json.loads(res.data)
        assert res.status_code == 404