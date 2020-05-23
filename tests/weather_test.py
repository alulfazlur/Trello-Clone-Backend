import json
from . import app, client, cache, create_token_internal, init_database
from unittest import mock
from unittest.mock import patch

class TestWeatherCrud():

    def mocked_requests_get(*args, **kwargs):
        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code
            
            def json(self):
                return self.json_data

        if len(args) > 0:
            if args[0] == app.config['WIO_HOST']+"/ip":
                return MockResponse({
                                        "latitude": 81292980931,
                                        "longitude": 91209381092,
                                        "city":"Malang",
                                        "organization":"Maxindo",
                                        "timezone":"Asia/Jakarta"
                                    }, 200)
            elif args[0] == app.config['WIO_HOST']+"/current":
                return MockResponse({
                                        "data": [
                                            {
                                                "datetime":"27 Jan 2017",
                                                "temp": 27
                                            }
                                        ]
                                    }, 200)
        else:
            return MockResponse(None, 404)

    # @mock.patch('requests.post', side_effect=mocked_requests_post)
    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_check_weather_ip(self, get_mock, client, init_database):
        token = create_token_internal()
        res = client.get(
            '/weather/ip',
            query_string={"ip":"167.520.430"}, 
            headers={'Authorization':'Bearer ' + token}
            )
        res_json = json.loads(res.data)
        assert res.status_code == 200

