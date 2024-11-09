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
    post = db.relationship("Post", foreign_keys=[pid], viewonly=True)
    user = db.relationship("User", foreign_keys=[uid], viewonly=True)
    __table_args__ = (PrimaryKeyConstraint(uid, pid), {})

class Upvote(db.Model):
    uid = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    pid = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    post = db.relationship("Post", foreign_keys=[pid], viewonly=True)
    user = db.relationship("User", foreign_keys=[uid], viewonly=True)
    __table_args__ = (PrimaryKeyConstraint(uid, pid), {})

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    notifications = db.relationship("Post", secondary=Notification.__table__)

class ImageFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(30), unique=True, nullable=False)

class VideoLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rid = db.Column(db.Integer, nullable=True)
    pid = db.Column(db.Integer, db.ForeignKey('post.id'))
    content = db.Column(db.UnicodeText, nullable=True, default='')
    image = db.Column(db.String(120), unique=True, nullable=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    deleted_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=None)
    deleted_at = db.Column(db.DateTime, default=None)
    created_by = db.relationship("User", foreign_keys=[created_by_id])
    updated_by = db.relationship("User", foreign_keys=[updated_by_id])
    deleted_by = db.relationship("User", foreign_keys=[deleted_by_id])
    level = db.Column(db.Integer, nullable=False,  default=0)
    comments = db.Column(db.Integer, nullable=False,  default=0)
    upvotes = db.relationship("User", secondary=Upvote.__table__)
    children = []
    def __repr__(self):
        return f'<Post id={self.id} pid={self.pid} rid={self.rid}>'

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reason = db.Column(db.String(60), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reported_post = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    created_by = db.relationship("User", foreign_keys=[created_by_id])
    post = db.relationship("Post", foreign_keys=[reported_post])
