import json, hashlib, uuid
from datetime import datetime
from blueprints import db, app, user_required

from flask import Blueprint
from flask_restful import Resource, Api, reqparse, marshal, inputs
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt_claims
from sqlalchemy import desc

from .model import Lists
from blueprints.card.model import Cards
from blueprints.card.model import CardMembers
from blueprints.board.model import Boards

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

        salt = uuid.uuid4()
        code = ('%s%s' % (args['title'], salt)).encode('utf-8')

        qry = Lists(args['boardId'], args['title'], order, code)
        db.session.add(qry)
        db.session.commit()

        app.logger.debug('DEBUG : %s', qry)

        return marshal(qry, Lists.response_fields), 200, {'Content-Type': 'application/json'}

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', location='args')
        args = parser.parse_args()

        qry = Lists.query.get(args['id'])
        if qry is None:
            return {'status': 'LIST_NOT_FOUND'}, 404
        
        cardQry = Cards.query.filter_by(listId=args["id"]).order_by(Cards.order).all()
        marhsalList = marshal(qry, Lists.response_fields)
        cards=[]
        for card in cardQry:
            marshalCard = marshal(card, Cards.response_fields)
            cardMembers = CardMembers.query.filter_by(cardId=card.id).order_by(CardMembers.memberId).all()
            members=[]
            for member in cardMembers:
                marshalMember = marshal(member, CardMembers.response_fields)
                members.append(marshalMember)
            marshalCard["members"] = members
            cards.append(marshalCard)
        marhsalList["cards"]=cards
        return marhsalList, 200

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

class ListReorder(Resource):
	def options(self, id=None):
		return {'status': 'ok'}, 200

	@user_required
	def put(self):
		parser = reqparse.RequestParser()
		parser.add_argument('code', location='json', required=True)
		parser.add_argument('boardId', location='json', required=True)
		parser.add_argument('order', location='json')
		args = parser.parse_args()

		qry = Lists.query.filter_by(code=args['code']).first()
		if qry is None:
			return {'status': 'LIST_NOT_FOUND'}, 404
		
		thisOrder = qry.order
		# Jika dipindah tapi berada di list yang sama
		if args["boardId"] == qry.boardId:
			if args['order'] is not None:
				newOrder = int(args['order'])
				listinBoard = Lists.query.filter_by(boardId=args["boardId"]).all()
				for listQry in listinBoard :
					# Jika dipindah kebawah
					if newOrder > thisOrder :
						if listQry.order <= newOrder and listQry.order > thisOrder:
							listQry.order -= 1
							db.session.commit()
					# Jika dipindah keatas
					elif newOrder < thisOrder :
						if listQry.order >= newOrder and listQry.order < thisOrder:
							listQry.order += 1
							db.session.commit()
				qry.order = args['order']
				db.session.commit()
		
		# Jika dipindah tapi berada di list yang berbeda
		elif args["boardId"] != qry.boardId:
			listInOldBoard = Lists.query.filter_by(boardId=qry.boardId).all()
			# Jika order di list lama dibawah yang dipindah, maka order -1
			for listQry in listInOldBoard :
				if listQry.order > int(qry.order) :
					listQry.order -= 1
					db.session.commit()

			if args['order'] is None:
				listInNewBoard = Lists.query.filter_by(boardId=args["boardId"]).all()
				qry.order = len(listInNewBoard)
				db.session.commit()
				
			if args['order'] is not None:
				listInNewBoard = Lists.query.filter_by(boardId=args["boardId"]).all()
				for listQry in listInNewBoard:
					if int(args['order']) <= listQry.order:
						listQry.order += 1
						db.session.commit()
				qry.order = args['order']
			qry.boardId = args["boardId"]
			db.session.commit()

		return marshal(qry, Lists.response_fields), 200, {'Content-Type': 'application/json'}

class AllList(Resource):
    def options(self, id=None):
        return {'status': 'ok'}, 200

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('boardId', location='args')
        args = parser.parse_args()

        listsQry = Lists.query.filter_by(boardId=args['boardId']).order_by(Lists.order).all()
        if listsQry is None:
            return {'status': 'LISTS_NOT_FOUND'}, 404

        allLists = []
        for data in listsQry:
            marshalData = marshal(data, Lists.response_fields)
            listId = data.id
            cardInList = Cards.query.filter_by(listId=listId).order_by(Cards.order).all()
            cards=[]
            for card in cardInList:
                marshalCard = marshal (card, Cards.response_fields)
                cards.append(marshalCard)
            marshalData['cards'] = cards
            allLists.append(marshalData)
        return allLists, 200


api.add_resource(ListResource, '')
api.add_resource(ListReorder, '/reorder')
api.add_resource(AllList, '/list')
