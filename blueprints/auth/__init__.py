from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from functools import wraps

from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt_claims

from blueprints.user.model import Users
import hashlib

from blueprints import user_required

bp_auth = Blueprint('auth', __name__)
api = Api(bp_auth)


class CreateTokenResource(Resource):
    def options(self, id=None):
        return {'status': 'ok'}, 200

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', location='args', required=True)
        parser.add_argument('password', location='args', required=True)
        args = parser.parse_args()

        qry_client = Users.query.filter_by(username=args['username']).first()
        if qry_client is not None:
            client_salt = qry_client.salt
            encoded = ('%s%s' % (args['password'], client_salt)).encode('utf-8')
            hash_pass = hashlib.sha512(encoded).hexdigest()
            if hash_pass == qry_client.password and qry_client.username == args['username']:
                qry_client = marshal(qry_client, Users.jwt_user_fields)
                qry_client['identifier'] = "sevoucher"
                token = create_access_token(
                    identity=args['username'], user_claims=qry_client)
                return {'token': token}, 200

            return {'status': 'UNAUTHORIZED', 'message': 'invalid key or secret'}, 404

class RefreshTokenResource(Resource):
    def options(self, id=None):
        return {'status': 'ok'}, 200

    def post(self):
        current_user = get_jwt_identity()
        claims = get_jwt_claims()
        token = create_access_token(identity=current_user, user_claims=claims)
        return {'token': token}, 200


api.add_resource(CreateTokenResource, '')
api.add_resource(RefreshTokenResource, '/refresh')
