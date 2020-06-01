import json, hashlib, uuid
from datetime import datetime
from blueprints import db, app, user_required

from flask import Blueprint
from flask_restful import Resource, Api, reqparse, marshal, inputs
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt_claims
from sqlalchemy import desc

from .model import Cards, CardMembers, CardLabels
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
		parser.add_argument('text', location='json', required=True)
		args = parser.parse_args()

		lastOrder = Cards.query.filter_by(listId=args["listId"]).all()
		if lastOrder is None :
			order = 0
		else : 
			order = len(lastOrder)
			
		salt = uuid.uuid4()
		code = ('%s%s' % (args['text'], salt)).encode('utf-8')
		qry = Cards(args['listId'], args['text'], order, code)
		db.session.add(qry)
		db.session.commit()

		app.logger.debug('DEBUG : %s', qry)

		return marshal(qry, Cards.response_fields), 200, {'Content-Type': 'application/json'}

	def get(self):
		parser = reqparse.RequestParser()
		parser.add_argument('cardId', location='args')
		args = parser.parse_args()

		qry = Cards.query.get(args['cardId'])
		if qry is None:
			return {'status': 'CARD_NOT_FOUND'}, 404
		
		marshalQry = marshal(qry, Cards.response_fields)

		members = CardMembers.query.filter_by(cardId=args["cardId"]).all()
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
		parser.add_argument('listId', location='json', required=True)
		parser.add_argument('text', location='json')
		parser.add_argument('order', location='json')
		parser.add_argument('description', location='json')
		parser.add_argument('cover', location='json')
		args = parser.parse_args()

		qry = Cards.query.get(args['id'])
		if qry is None:
			return {'status': 'CARD_NOT_FOUND'}, 404

		if args['text'] is not None:
			qry.text = args['text']
		if args['description'] is not None:
			qry.description = args['description']
		if args['cover'] is not None:
			qry.cover = args['cover']
		db.session.commit()
		
		thisOrder = qry.order
		# Jika dipindah tapi berada di list yang sama
		if int(args['listId']) == qry.listId:
			if args['order'] is not None:
				newOrder = int(args['order'])
				cardInList = Cards.query.filter_by(listId=args["listId"]).all()
				for card in cardInList :
					# Jika dipindah kebawah
					if newOrder > thisOrder :
						if card.order <= newOrder and card.order > thisOrder:
							card.order -= 1
							db.session.commit()
					# Jika dipindah keatas
					elif newOrder < thisOrder :
						if card.order >= newOrder and card.order < thisOrder:
							card.order += 1
							db.session.commit()
				qry.order = args['order']
				db.session.commit()
		
		# Jika dipindah tapi berada di list yang berbeda
		elif int(args['listId']) != qry.listId:
			cardInOldList = Cards.query.filter_by(listId=qry.listId).all()
			# Jika order di list lama dibawah yang dipindah, maka order -1
			for card in cardInOldList :
				if card.order > int(qry.order) :
					card.order -= 1
					db.session.commit()

			if args['order'] is None:
				cardInNewList = Cards.query.filter_by(listId=args['listId']).all()
				qry.order = len(cardInNewList)
				db.session.commit()
				
			if args['order'] is not None:
				cardInNewList = Cards.query.filter_by(listId=args["listId"]).all()
				for card in cardInNewList:
					if int(args['order']) <= card.order:
						card.order += 1
						db.session.commit()
				qry.order = args['order']
			qry.listId = args['listId']
			db.session.commit()

		return marshal(qry, Cards.response_fields), 200, {'Content-Type': 'application/json'}

	@user_required
	def delete(self):
		parser = reqparse.RequestParser()
		parser.add_argument('id', location='json', required=True)
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

class CardReorder(Resource):
	def options(self, id=None):
		return {'status': 'ok'}, 200

	@user_required
	def put(self):
		parser = reqparse.RequestParser()
		parser.add_argument('code', location='json', required=True)
		parser.add_argument('listCode', location='json', required=True)
		parser.add_argument('order', location='json')
		args = parser.parse_args()

		qry = Cards.query.filter_by(code=args['code']).first()
		if qry is None:
			return {'status': 'CARD_NOT_FOUND'}, 404
		
		thisOrder = qry.order
		listQry = Lists.query.filter_by(code=args["listCode"]).first()
		listId = listQry.id
		# Jika dipindah tapi berada di list yang sama
		if listId == qry.listId:
			if args['order'] is not None:
				newOrder = int(args['order'])
				listQry = Lists.query.filter_by(code=args["listCode"]).first()
				listId = listQry.id
				cardInList = Cards.query.filter_by(listId=listId).all()
				for card in cardInList :
					# Jika dipindah kebawah
					if newOrder > thisOrder :
						if card.order <= newOrder and card.order > thisOrder:
							card.order -= 1
							db.session.commit()
					# Jika dipindah keatas
					elif newOrder < thisOrder :
						if card.order >= newOrder and card.order < thisOrder:
							card.order += 1
							db.session.commit()
				qry.order = args['order']
				db.session.commit()
		
		# Jika dipindah tapi berada di list yang berbeda
		elif listId != qry.listId:
			cardInOldList = Cards.query.filter_by(listId=qry.listId).all()
			# Jika order di list lama dibawah yang dipindah, maka order -1
			for card in cardInOldList :
				if card.order > int(qry.order) :
					card.order -= 1
					db.session.commit()

			if args['order'] is None:
				listQry = Lists.query.filter_by(code=args["listCode"]).first()
				listId = listQry.id
				cardInNewList = Cards.query.filter_by(listId=listId).all()
				qry.order = len(cardInNewList)
				db.session.commit()
				
			if args['order'] is not None:
				listQry = Lists.query.filter_by(code=args["listCode"]).first()
				listId = listQry.id
				cardInNewList = Cards.query.filter_by(listId=listId).all()
				for card in cardInNewList:
					if int(args['order']) <= card.order:
						card.order += 1
						db.session.commit()
				qry.order = args['order']
			qry.listId = listId
			db.session.commit()

		return marshal(qry, Cards.response_fields), 200, {'Content-Type': 'application/json'}
	

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
		check= CardMembers.query.filter_by(cardId=args["cardId"], memberId=memberId).first()
		if check is None :
			qry = CardMembers(args['cardId'], memberId)
			db.session.add(qry)
			db.session.commit()
			app.logger.debug('DEBUG : %s', qry)
			return marshal(qry, CardMembers.response_fields), 200, {'Content-Type': 'application/json'}
			# membersQry = CardMembers.query.filter_by(cardId=args["cardId"]).all()
			# cardmembers = []
			# for member in membersQry:
			# 	memberProfile = Users.query.get(member.memberId)
			# 	marshalMemberProfile = marshal(memberProfile, Users.response_fields)
			# 	cardmembers.append(marshalMemberProfile)
			# return cardmembers, 200, {'Content-Type': 'application/json'}
		return {'status': 'MEMBER_IS_EXIST'}, 400
		
	def get(self):
		parser = reqparse.RequestParser()
		parser.add_argument('id', location='args', required=True)
		args = parser.parse_args()

		qry = CardMembers.query.get(args["id"])
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

		membersQry = CardMembers.query.filter_by(cardId=args["cardId"]).all()
		cardmembers = []
		for member in membersQry:
			memberProfile = Users.query.get(member.memberId)
			marshalMemberProfile = marshal(memberProfile, Users.response_fields)
			cardmembers.append(marshalMemberProfile)
		return cardmembers, 200, {'Content-Type': 'application/json'}

class CardMemberList(Resource):
	def options(self, id=None):
		return {'status': 'ok'}, 200

	def get(self):
		parser = reqparse.RequestParser()
		parser.add_argument('cardId', location='args', required=True)
		args = parser.parse_args()

		membersQry = CardMembers.query.filter_by(cardId=args["cardId"]).all()
		cardmembers = []
		for member in membersQry:
			memberProfile = Users.query.get(member.memberId)
			marshalMemberProfile = marshal(memberProfile, Users.response_fields)
			cardmembers.append(marshalMemberProfile)
		return cardmembers, 200, {'Content-Type': 'application/json'}

class CardLabelResource(Resource):
	def options(self, id=None):
		return {'status': 'ok'}, 200

	@user_required
	def post(self):
		parser = reqparse.RequestParser()
		parser.add_argument('cardId', location='json', required=True)
		parser.add_argument('label', location='json', required=True)
		args = parser.parse_args()

		check= CardLabels.query.filter_by(cardId=args["cardId"], label=args["label"]).first()
		if check is None :
			qry = CardLabels(args['cardId'], args["label"])
			db.session.add(qry)
			db.session.commit()
			app.logger.debug('DEBUG : %s', qry)
			return marshal(qry, CardLabels.response_fields), 200, {'Content-Type': 'application/json'}
			# labelsQry = CardLabels.query.filter_by(cardId=args["cardId"]).all()
			# cardLabels =[]
			# for label in labelsQry:
			# 	marshalLabel = marshal(label, CardLabels.response_fields)
			# 	cardLabels.append(marshalLabel)
			# return cardLabels, 200, {'Content-Type': 'application/json'}
		return {'status': 'LABEL_IS_EXIST'}, 400
		
	def get(self):
		parser = reqparse.RequestParser()
		parser.add_argument('id', location='args', required=True)
		args = parser.parse_args()

		qry = CardLabels.query.get(args["id"])
		return marshal(qry, CardLabels.response_fields), 200, {'Content-Type': 'application/json'}
	
	@user_required
	def delete(self):
		parser = reqparse.RequestParser()
		parser.add_argument('cardId', location='json', required=True)
		parser.add_argument('label', location='json', required=True)
		args = parser.parse_args()

		qry = CardLabels.query.filter_by(cardId=args["cardId"], label=args["label"]).first()

		db.session.delete(qry)
		db.session.commit()

		cardLabels =[]
		labelsQry = CardLabels.query.filter_by(cardId=args["cardId"]).all()
		for label in labelsQry:
			marshalLabel = marshal(label, CardLabels.response_fields)
			cardLabels.append(marshalLabel)
		return cardLabels, 200, {'Content-Type': 'application/json'}

class CardLabelList(Resource):
	def options(self, id=None):
		return {'status': 'ok'}, 200

	def get(self):
		parser = reqparse.RequestParser()
		parser.add_argument('cardId', location='args', required=True)
		args = parser.parse_args()

		labelsQry = CardLabels.query.filter_by(cardId=args["cardId"]).all()
		cardLabels =[]
		for label in labelsQry:
			marshalLabel = marshal(label, CardLabels.response_fields)
			cardLabels.append(marshalLabel)
		return cardLabels, 200, {'Content-Type': 'application/json'}

api.add_resource(CardResource, '')
api.add_resource(CardList, '/list')
api.add_resource(CardReorder, '/reorder')
api.add_resource(CardMemberList, '/member/list')
api.add_resource(CardMemberResource, '/member')
api.add_resource(CardLabelList, '/label/list')
api.add_resource(CardLabelResource, '/label')
