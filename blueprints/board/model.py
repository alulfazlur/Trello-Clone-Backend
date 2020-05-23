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


class Boards(db.Model):
    __tablename__ = "boards"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ownerId = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    memberIds = db.Column(db.Integer)
    background = db.Column(db.String(255), nullable=False, default="green")
    description = db.Column(LONGTEXT(charset='latin1'))

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    boardId = db.relationship(
		'Lists', backref='boards', lazy=True, uselist=False, cascade="all, delete-orphan")

    response_fields = {
        'id': fields.Integer,
        'ownerId': fields.String,
        'title': fields.String,
        'memberIds': fields.String,
        'background': fields.String,
        'description': fields.String,
    }

    def __init__(self, ownerId, title):
        self.ownerId = ownerId
        self.title = title
        # self.background = background

    def __repr__(self):
        return '<Boards %r>' % self.id
