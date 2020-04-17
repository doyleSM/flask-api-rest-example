from flask import request, url_for
from db import db
from libs.mailgun import Mailgun


class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    activated = db.Column(db.Boolean, default=False)

    @classmethod
    def find_by_username(cls, username: str):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email: str):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_id(cls, _id: int):
        return cls.query.filter_by(id=_id).first()

    def send_confirmation_email(self):
        link = request.url_root[:-1] + url_for("userconfirm", user_id=self.id)
        subject = "Registration confirmation"
        text = f"Por gentileza, confirme seu email clicando aqui {link}"
        html = f"<html>Por gentileza, confirme seu email clicando {link}</html>"
        return Mailgun.send_email(self.email, subject, text, html)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
