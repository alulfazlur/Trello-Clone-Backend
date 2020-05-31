from flask_restful import fields
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import text
from datetime import datetime

from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref
from blueprints import db


class Lists(db.Model):
    __tablename__ = "lists"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    boardId = db.Column(db.Integer, db.ForeignKey("boards.id", ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    cards = db.Column(db.String(255))
    code = db.Column(db.String(255))
    # archived = db.Column(db.Boolean, default=False, server_default="false")

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    listId = db.relationship('Cards', backref='lists', lazy=True, uselist=False, cascade="all, delete-orphan", passive_deletes=True)

    response_fields = {
        'id': fields.Integer,
        'boardId': fields.Integer,
        'title': fields.String,
        'order': fields.Integer,
        'cards': fields.Integer,
        # 'archived': fields.Integer,
        'code': fields.String,
    }

    def __init__(self, boardId, title, order, code):
        self.boardId = boardId
        self.title = title
        self.order = order
        self.code = code

    def __repr__(self):
        return '<Lists %r>' % self.id
