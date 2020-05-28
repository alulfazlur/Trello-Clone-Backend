import json, hashlib, uuid
from datetime import datetime
from blueprints import db, app, user_required

from flask import Blueprint
from flask_restful import Resource, Api, reqparse, marshal, inputs
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt_claims
from sqlalchemy import desc

from .model import Boards
from blueprints.list.model import Lists
from blueprints.card.model import Cards
from blueprints.card.model import CardMembers

bp_board = Blueprint('board', __name__)
api = Api(bp_board)


class BoardResource(Resource):
    def options(self, id=None):
        return {'status': 'ok'}, 200

    @user_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('title', location='json', required=True)
        parser.add_argument('background', location='json')
        args = parser.parse_args()

        claims = get_jwt_claims()
        ownerId = claims['id']

        qry = Boards(ownerId, args['title'])
        db.session.add(qry)
        db.session.commit()
            
        app.logger.debug('DEBUG : %s', qry)

        return marshal(qry, Boards.response_fields), 200, {'Content-Type': 'application/json'}

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', location='args')
        args = parser.parse_args()

        qry = Boards.query.get(args['id'])
        if qry is None:
            return {'status': 'BOARD_NOT_FOUND'}, 404

        marshalBoard = marshal(qry, Boards.response_fields)
        listId = qry.id
        listInBoard = Lists.query.filter_by(boardId=args["id"]).order_by(Lists.order).all()
        lists=[]
        for listQry in listInBoard:
            marshalList = marshal (listQry, Lists.response_fields)
            lists.append(marshalList)
        marshalBoard['lists'] = lists
        return marshalBoard, 200

    @user_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', location='json', required=True)
        parser.add_argument('title', location='json')
        parser.add_argument('background', location='json')
        parser.add_argument('description', location='json')
        args = parser.parse_args()

        qry = Boards.query.get(args['id'])
        if qry is None:
            return {'status': 'BOARD_NOT_FOUND'}, 404

        if args['title'] is not None:
            qry.title = args['title']
        if args['background'] is not None:
            qry.background = args['background']
        if args['description'] is not None:
            qry.description = args['description']
        db.session.commit()

        return marshal(qry, Boards.response_fields), 200, {'Content-Type': 'application/json'}

    @user_required
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', location='args', required=True)
        args = parser.parse_args()

        qry = Boards.query.get(args['id'])
        if qry is None:
            return {'status': 'BOARD_NOT_FOUND'}, 404

        db.session.delete(qry)
        db.session.commit()

        return {'status': 'BOARD_DELETED'}, 200


class BoardList(Resource):
    def options(self, id=None):
        return {'status': 'ok'}, 200

    @user_required
    def get(self):
        # parser = reqparse.RequestParser()
        # parser.add_argument('ownerId', location='args')
        # args = parser.parse_args()

        claims = get_jwt_claims()
        ownerId = claims['id']

        boardList = Boards.query.filter_by(ownerId=ownerId).all()
        if boardList is None:
            return {'status': 'BOARD_NOT_FOUND'}, 404
        boards = []
        for board in boardList:
            marshalBoard = marshal(board, Boards.response_fields)
            listInBoard = Lists.query.filter_by(boardId=board.id).order_by(Lists.order).all()
            lists=[]
            for listQry in listInBoard:
                marshalList = marshal(listQry, Lists.response_fields)
                cardInList = Cards.query.filter_by(listId=listQry.id).order_by(Cards.order).all()
                cards=[]
                for card in cardInList:
                    marshalCard = marshal(card, Cards.response_fields)
                    cardMembers = CardMembers.query.filter_by(cardId=card.id).order_by(CardMembers.memberId).all()
                    members =[]
                    for member in cardMembers:
                        marshalMember = marshal(member, CardMembers.response_fields)
                        members.append(marshalMember)
                    marshalCard["members"]=members
                    cards.append(marshalCard)
                marshalList["cards"]=cards
                lists.append(marshalList)
            marshalBoard['lists'] = lists
            boards.append(marshalBoard)
        return boards, 200


api.add_resource(BoardResource, '')
api.add_resource(BoardList, '/list')
