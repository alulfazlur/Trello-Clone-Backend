from flask_restful import fields
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import text
from datetime import datetime

from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref
from blueprints import db


class Comments(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cardId = db.Column(db.Integer, db.ForeignKey("boards.id"), nullable=False)
    userId = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    comment = db.Column(db.LONGTEXT(charset='latin1'), nullable=False)

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    response_fields = {
        'id': fields.Integer,
        'cardId': fields.Integer,
        'userId': fields.String,
        'comment': fields.Integer,
    }

    def __init__(self, cardId, userId, comment):
        self.cardId = cardId
        self.userId = userId
        self.comment = comment

    def __repr__(self):
        return '<Comments %r>' % self.id
