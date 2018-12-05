"""API db models"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import TIMESTAMP, TINYINT
from sqlalchemy import UniqueConstraint
from flask_login import UserMixin
from werkzeug.security import check_password_hash
from datetime import datetime

db = SQLAlchemy()


class Users(db.Model, UserMixin):
    __tablename__ = 'USERS'
    id_user = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(255), default='')
    email = db.Column(db.String(255), unique=True, default='')
    username = db.Column(db.String(255), default='')
    qrcode_url = db.Column(db.String(500), default='')
    profile_img_url = db.Column(db.String(500), default='')
    id_user_hash = db.Column(db.String(255), unique=True, default='')
    is_vendor = db.Column(TINYINT(1), default=0)
    # TODO: Add unique=True for phone_number
    phone_no = db.Column(db.String(20), default='')
    create_timestamp = db.Column(
        TIMESTAMP, default=datetime.utcnow().replace(microsecond=0))

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_id(self):
        return self.id_user_hash


class Items(db.Model):
    __tablename__ = 'ITEMS'
    __table_args__ = (UniqueConstraint('id_user', 'item_name'),)
    id_item = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey(
        'USERS.id_user', ondelete='RESTRICT', onupdate='RESTRICT'))
    item_name = db.Column(db.String(255), default='')
    description = db.Column(db.String(255), default='')
    category = db.Column(db.String(255), default='')
    price = db.Column(db.Float, default=0.0)
    image_url = db.Column(db.String(500), default='')
    order_count = db.Column(db.Integer, default=0)
    create_timestamp = db.Column(
        TIMESTAMP, default=datetime.utcnow().replace(microsecond=0))


class Tasks(db.Model):
    __tablename__ = 'TASKS'
    id_task = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey(
        'USERS.id_user', ondelete='RESTRICT', onupdate='RESTRICT'))
    id_cust = db.Column(db.Integer, db.ForeignKey(
        'USERS.id_user', ondelete='RESTRICT', onupdate='RESTRICT'))
    id_item = db.Column(db.Integer, db.ForeignKey(
        'ITEMS.id_item', ondelete='RESTRICT', onupdate='RESTRICT'))
    id_table = db.Column(db.Integer)
    order_count = db.Column(db.Integer)
    create_timestamp = db.Column(
        TIMESTAMP, default=datetime.utcnow().replace(microsecond=0))


class FCM_Access_Token(db.Model):
    __table_args__ = (UniqueConstraint('id_user', 'access_token'),)
    __tablename__ = "FCM_ACCESS_TOKEN"
    id_token = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey(
        'USERS.id_user', ondelete='RESTRICT', onupdate='RESTRICT'))
    access_token = db.Column(db.String(255), default='')
    create_timestamp = db.Column(
        TIMESTAMP, default=datetime.utcnow().replace(microsecond=0))
