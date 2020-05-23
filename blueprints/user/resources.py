import json, hashlib, uuid
from datetime import datetime
from blueprints import db, app, user_required

from flask import Blueprint
from flask_restful import Resource, Api, reqparse, marshal, inputs
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt_claims
from sqlalchemy import desc

from .model import Users

bp_user = Blueprint('user', __name__)
api = Api(bp_user)


class UserResourceSignUp(Resource):
    def options(self, id=None):
        return {'status': 'ok'}, 200

    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('username', location='json', required=True)
        parser.add_argument('password', location='json', required=True)
        parser.add_argument('name', location='json', required=True)
        parser.add_argument('email', location='json', required=True)
        # parser.add_argument('avatar', location='json')

        args = parser.parse_args()

        salt = uuid.uuid4().hex
        encoded = ('%s%s' % (args['password'], salt)).encode('utf-8')
        hash_pass = hashlib.sha512(encoded).hexdigest()

        user = Users(args['username'], hash_pass, args['name'], args['email'],
                    #  args['avatar'],
                     salt)
        db.session.add(user)
        db.session.commit()

        app.logger.debug('DEBUG : %s', user)

        return marshal(user, Users.response_fields), 200, {'Content-Type': 'application/json'}


class UserResource(Resource):
    def options(self, id=None):
        return {'status': 'ok'}, 200

    @user_required
    def get(self):
        claims = get_jwt_claims()
        userId = claims['id']
        qry = Users.query.filter_by(id=userId).first()
        if qry is not None:
            return marshal(qry, Users.response_fields), 200
        return {'status': 'NOT_FOUND'}, 404

    @user_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', location='json')
        parser.add_argument('email', location='json')
        parser.add_argument('avatar', location='json')
        args = parser.parse_args()

        claims = get_jwt_claims()
        userId = claims['id']
        qry = Users.query.filter_by(id=userId).first()

        if args['name'] is not None:
            qry.name = args['name']
        if args['email'] is not None:
            qry.email = args['email']
        if args['avatar'] is not None:
            qry.avatar = args['avatar']
        db.session.commit()

        return marshal(qry, Users.response_fields), 200, {'Content-Type': 'application/json'}


class UserDeleteResource(Resource):
    def options(self, id=None):
        return {'status': 'ok'}, 200

    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', location='args', required=True)
        args = parser.parse_args()
        qry = Users.query.filter_by(username=args['username']).first()
        if qry is None:
            return {'status': 'NOT_FOUND'}, 404

        db.session.delete(qry)
        db.session.commit()

        return {'status': 'DELETED'}, 200


class UserList(Resource):
    def options(self, id=None):
        return {'status': 'ok'}, 200

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('p', type=int, location='args', default=1)
        parser.add_argument('rp', type=int, location='args', default=25)
        parser.add_argument('orderby', location='args',
                            help='invalid orderby value', choices=('id', 'name'))
        parser.add_argument('sort', location='args',
                            help='invalid sort value', choices=('desc', 'asc'))

        args = parser.parse_args()

        offset = (args['p'] * args['rp'] - args['rp'])

        qry = Users.query

        # Orderby
        if args['orderby'] is not None:
            if args['orderby'] == 'id':
                if args['sort'] == 'desc':
                    qry = qry.order_by(desc(Users.id))
                else:
                    qry = qry.order_by(Users.id)

            elif args['orderby'] == 'user_id':
                if args['sort'] == 'desc':
                    qry = qry.order_by(desc(Users.user_id))
                else:
                    qry = qry.order_by(Users.user_id)

            else:
                if args['sort'] == 'desc':
                    qry = qry.order_by(desc(Users.name))
                else:
                    qry = qry.order_by(Users.name)

        rows = []
        for row in qry.limit(args['rp']).offset(offset).all():
            rows.append(marshal(row, Users.response_fields))

        return rows, 200


api.add_resource(UserList, '/list')
api.add_resource(UserResourceSignUp, '')
api.add_resource(UserDeleteResource, '/delete')
api.add_resource(UserResource, '/me')
