from flask_restful import fields
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import text
from datetime import datetime

from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref
from blueprints import db


class Cards(db.Model):
    __tablename__ = "cards"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    listId = db.Column(db.Integer, db.ForeignKey("lists.id", ondelete='CASCADE'), nullable=False)
    text = db.Column(db.String(255), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    description = db.Column(LONGTEXT(charset='latin1'))
    members = db.Column(db.String(255))
    code = db.Column(db.String(255))
    labels = db.Column(db.String(255))
    cover = db.Column(db.String(255))
    
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    cardId = db.relationship(
		'CardMembers', backref='cards', lazy=True, uselist=False, cascade="all, delete-orphan", passive_deletes=True)
    cardId = db.relationship(
		'CardLabels', backref='cards', lazy=True, uselist=False, cascade="all, delete-orphan", passive_deletes=True)

    response_fields = {
        'id': fields.Integer,
        'listId': fields.Integer,
        'text': fields.String,
        'order': fields.Integer,
        'members': fields.String,
        'code': fields.String,
        'labels': fields.String,
        'cover': fields.String,
    }

    def __init__(self, listId, text, order, code):
        self.listId = listId
        self.text = text
        self.order = order
        self.code = code

    def __repr__(self):
        return '<Cards %r>' % self.id


class CardMembers(db.Model):
    __tablename__ = "card_members"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cardId = db.Column(db.Integer, db.ForeignKey("cards.id", ondelete='CASCADE'), nullable=False)
    memberId = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    response_fields = {
        'id': fields.Integer,
        'cardId': fields.Integer,
        'memberId': fields.String,
    }

    def __init__(self, cardId, memberId):
        self.cardId = cardId
        self.memberId = memberId

    def __repr__(self):
        return '<CardMembers %r>' % self.id

class CardLabels(db.Model):
    __tablename__ = "card_labels"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cardId = db.Column(db.Integer, db.ForeignKey("cards.id", ondelete='CASCADE'), nullable=False)
    label = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    response_fields = {
        'id': fields.Integer,
        'cardId': fields.Integer,
        'label': fields.String,
    }

    def __init__(self, cardId, label):
        self.cardId = cardId
        self.label = label

    def __repr__(self):
        return '<CardLabels %r>' % self.id