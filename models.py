from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_bcrypt import Bcrypt
from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy.schema import PrimaryKeyConstraint
from sqlalchemy.orm import relationship

db = SQLAlchemy()
bcrypt = Bcrypt()

class Notification(db.Model):
    uid = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    pid = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    __table_args__ = (PrimaryKeyConstraint(uid, pid), {})

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    notifications = db.relationship("Post", secondary=Notification.__table__)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rid = db.Column(db.Integer, nullable=True)
    pid = db.Column(db.Integer, db.ForeignKey('post.id'))
    content = db.Column(db.UnicodeText, nullable=True, default='')
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.relationship("User", foreign_keys=[created_by_id])
    level = db.Column(db.Integer, nullable=False,  default=0)
    comments = db.Column(db.Integer, nullable=False,  default=0)
    children = []
    def __repr__(self):
        return f'<Post id={self.id} pid={self.pid} rid={self.rid}>'
