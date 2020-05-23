import json, hashlib, uuid
from datetime import datetime
from blueprints import db, app, user_required

from flask import Blueprint
from flask_restful import Resource, Api, reqparse, marshal, inputs
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt_claims
from sqlalchemy import desc

from .model import Lists

bp_list = Blueprint('list', __name__)
api = Api(bp_list)


class ListResource(Resource):
    def options(self, id=None):
        return {'status': 'ok'}, 200

    @user_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('boardId', location='json', required=True)
        parser.add_argument('title', location='json', required=True)
        args = parser.parse_args()

        lastOrder = Lists.query.filter_by(boardId=args["boardId"]).all()
        if lastOrder is None :
            order = 0
        else : 
            order = len(lastOrder)

        qry = Lists(args['boardId'], args['title'], order)
        db.session.add(qry)
        db.session.commit()

        app.logger.debug('DEBUG : %s', qry)

        return marshal(qry, Lists.response_fields), 200, {'Content-Type': 'application/json'}

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', location='args')
        args = parser.parse_args()

        qry = Lists.query.get(args['id'])
        if qry is not None:
            return marshal(qry, Lists.response_fields), 200
        return {'status': 'LIST_NOT_FOUND'}, 404

    @user_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', location='json', required=True)
        parser.add_argument('boardId', location='json')
        parser.add_argument('title', location='json')
        parser.add_argument('order', location='json')
        args = parser.parse_args()

        qry = Lists.query.get(args['id'])
        if qry is None:
            return {'status': 'LITS_NOT_FOUND'}, 404


        if args['boardId'] is not None:
            qry.boardId = args['boardId']
        if args['title'] is not None:
            qry.title = args['title']
        
        if args['order'] is not None:
            listOrder = Lists.query.filter_by(boardId=args["boardId"]).all()
            thisOrder = Lists.query.get(args["id"]).order
            for lists in listOrder:
                # Jika dipindah kebawah
                if int(args['order']) >= thisOrder and lists.order >= thisOrder:
                    lists.order -= 1
                    db.session.commit()
                # Jika dipindah keatas
                elif int(args['order']) < thisOrder and lists.order <= thisOrder:
                    lists.order += 1
                    db.session.commit()
                    
            qry.order = args['order']
        db.session.commit()
        return marshal(qry, Lists.response_fields), 200, {'Content-Type': 'application/json'}

    @user_required
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', location='args', required=True)
        args = parser.parse_args()

        qry = Lists.query.get(args['id'])
        if qry is None:
            return {'status': 'LIST_NOT_FOUND'}, 404

        db.session.delete(qry)
        db.session.commit()

        return {'status': 'LIST_DELETED'}, 200


class AllList(Resource):
    def options(self, id=None):
        return {'status': 'ok'}, 200

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('boardId', location='args')
        args = parser.parse_args()

        qry = Lists.query.filter_by(boardId=args['boardId']).all()
        if qry is not None:
            return marshal(qry, Lists.response_fields), 200
        return {'status': 'LISTS_NOT_FOUND'}, 404


api.add_resource(ListResource, '')
api.add_resource(AllList, '/list')
