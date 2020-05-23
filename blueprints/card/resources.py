import json, hashlib, uuid
from datetime import datetime
from blueprints import db, app, user_required

from flask import Blueprint
from flask_restful import Resource, Api, reqparse, marshal, inputs
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt_claims
from sqlalchemy import desc

from .model import Cards, CardMembers
from blueprints.list.model import Lists
from blueprints.board.model import Boards
from blueprints.user.model import Users
bp_card = Blueprint('card', __name__)
api = Api(bp_card)

class CardResource(Resource):
	def options(self, id=None):
		return {'status': 'ok'}, 200

	@user_required
	def post(self):
		parser = reqparse.RequestParser()
		parser.add_argument('listId', location='json', required=True)
		parser.add_argument('title', location='json', required=True)
		args = parser.parse_args()

		lastOrder = Cards.query.filter_by(listId=args["listId"]).all()
		if lastOrder is None :
			order = 0
		else : 
			order = len(lastOrder)

		qry = Cards(args['listId'], args['title'], order)
		db.session.add(qry)
		db.session.commit()

		app.logger.debug('DEBUG : %s', qry)

		return marshal(qry, Cards.response_fields), 200, {'Content-Type': 'application/json'}

	def get(self):
		parser = reqparse.RequestParser()
		parser.add_argument('id', location='args')
		args = parser.parse_args()

		qry = Cards.query.get(args['id'])
		if qry is None:
			return {'status': 'CARD_NOT_FOUND'}, 404
		
		marshalQry = marshal(qry, Cards.response_fields)

		members = CardMembers.query.filter_by(cardId=args["id"]).all()
		listMembers =[]
		for member in members:
			memberId = member.memberId
			profile = Users.query.get(memberId)
			marshalProfile = marshal(profile, Users.response_fields)
			listMembers.append(marshalProfile)
		marshalQry["members"] = listMembers

		return marshalQry, 200

	@user_required
	def put(self):
		parser = reqparse.RequestParser()
		parser.add_argument('id', location='json', required=True)
		parser.add_argument('listId', location='json')
		parser.add_argument('title', location='json')
		parser.add_argument('order', location='json')
		parser.add_argument('description', location='json')
		args = parser.parse_args()

		qry = Cards.query.get(args['id'])
		if qry is None:
			return {'status': 'CARD_NOT_FOUND'}, 404


		if args['listId'] is not None:
			qry.listId = args['listId']
		if args['title'] is not None:
			qry.title = args['title']
		if args['description'] is not None:
			qry.description = args['description']
		db.session.commit()

		if args['order'] is not None:
			cardOrder = Cards.query.filter_by(listId=args["listId"]).all()
			thisOrder = Cards.query.get(args["id"]).order
			for card in cardOrder:
				# Jika dipindah kebawah
				if int(args['order']) >= thisOrder and card.order >= thisOrder:
					card.order -= 1
					db.session.commit()
				# Jika dipindah keatas
				elif int(args['order']) < thisOrder and card.order <= thisOrder:
					card.order += 1
					db.session.commit()
					
			qry.order = args['order']
		db.session.commit()

		return marshal(qry, Cards.response_fields), 200, {'Content-Type': 'application/json'}

	@user_required
	def delete(self):
		parser = reqparse.RequestParser()
		parser.add_argument('id', location='args', required=True)
		args = parser.parse_args()

		qry = Cards.query.get(args['id'])
		if qry is None:
			return {'status': 'CARD_NOT_FOUND'}, 404

		db.session.delete(qry)
		db.session.commit()

		listId = qry.listId
		cardsInList = Cards.query.filter_by(listId=listId).all()

		thisOrder = qry.order
		for card in cardsInList:
			if card.order >= thisOrder:
				card.order -= 1
				db.session.commit()

		return {'status': 'CARD_DELETED'}, 200


class CardList(Resource):
	def options(self, id=None):
		return {'status': 'ok'}, 200

	def get(self):
		parser = reqparse.RequestParser()
		parser.add_argument('listId', location='args')
		args = parser.parse_args()

		cardInList = Cards.query.filter_by(listId=args['listId']).all()
		if cardInList is None:
			return {'status': 'CARDS_NOT_FOUND'}, 404

		cardList =[]
		for card in cardInList :
			cardId = card.id
			marshalCard = marshal(card, Cards.response_fields)
			members = CardMembers.query.filter_by(cardId=cardId).all()
			listMembers =[]
			for member in members:
				memberId = member.memberId
				profile = Users.query.get(memberId)
				marshalProfile = marshal(profile, Users.response_fields)
				listMembers.append(marshalProfile)
			marshalCard["members"] = listMembers
			cardList.append(marshalCard)
		return cardList, 200


class CardMemberResource(Resource):
	def options(self, id=None):
		return {'status': 'ok'}, 200

	@user_required
	def post(self):
		parser = reqparse.RequestParser()
		parser.add_argument('cardId', location='json', required=True)
		parser.add_argument('username', location='json', required=True)
		args = parser.parse_args()

		memberId = Users.query.filter_by(username=args["username"]).first().id
		qry = CardMembers(args['cardId'], memberId)
		db.session.add(qry)
		db.session.commit()

		app.logger.debug('DEBUG : %s', qry)

		return marshal(qry, CardMembers.response_fields), 200, {'Content-Type': 'application/json'}

	def get(self):
		parser = reqparse.RequestParser()
		parser.add_argument('cardId', location='json', required=True)
		args = parser.parse_args()

		qry = CardMembers.query.filter_by(cardId=args["cardId"])
		return marshal(qry, CardMembers.response_fields), 200, {'Content-Type': 'application/json'}
	
	@user_required
	def delete(self):
		parser = reqparse.RequestParser()
		parser.add_argument('cardId', location='json', required=True)
		parser.add_argument('username', location='json', required=True)
		args = parser.parse_args()

		memberId = Users.query.filter_by(username=args["username"]).first().id
		qry = CardMembers.query.filter_by(cardId=args["cardId"], memberId=memberId).first()

		db.session.delete(qry)
		db.session.commit()

		return {'status': 'CARD_MEMBER_DELETED'}, 200

api.add_resource(CardResource, '')
api.add_resource(CardList, '/list')
api.add_resource(CardMemberResource, '/member')
