from config import SERVICE_DATABASE
from sqlalchemy import Column, ForeignKey, Boolean, String, Integer, LargeBinary, Date
from werkzeug.security import generate_password_hash

"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, Session
from sqlalchemy_serializer import SerializerMixin


service_db = create_engine(f'sqlite:///{SERVICE_DATABASE}?check_same_thread=False', echo=True)
Base = declarative_base()
"""

from app import db


class ClientModel(db.Model):
    __tablename__ = 'clients'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    is_private = db.Column(db.Boolean, default=False)
    Record = db.relationship('RecordModel')

    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email, "is_private": self.is_private}


class OrganizationModel(db.Model):
    __tablename__ = 'organizations'

    id = db.Column(Integer, nullable=False, primary_key=True)
    title = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    limit = db.Column(db.Integer, default=10)
    image = db.Column(db.LargeBinary, default=b' ')
    sticker = db.Column(db.String(1), nullable=False, default="⭐")
    Record = db.relationship('RecordModel')

    def to_dict(self):
        return {"id": self.id, "title": self.title, "email": self.email, "limit": self.limit, "image": self.image, "sticker": self.sticker, "Record": self.Record}


class RecordModel(db.Model):
    __tablename__ = 'records'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    client = db.Column(db.Integer, ForeignKey('clients.id'), nullable=False)
    organization = db.Column(db.Integer, ForeignKey('organizations.id'), nullable=False)
    accumulated = db.Column(db.Integer, nullable=False, default=1)
    last_record_date = db.Column(db.Date, nullable=False)
    Organization = db.relationship('OrganizationModel')
    Client = db.relationship('ClientModel')

    def to_dict(self):
        return {"id": self.id, "client": self.client, "organization": self.organization, "accumulated": self.accumulated, "last_record_date": self.last_record_date}


class AdminModel(db.Model):
    __tablename__ = 'admins'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    can_edit = db.Column(db.Boolean, nullable=False)


"""
def add_admin():
    email: str = input("email: ")
    password: str = input("password: ")
    can_edit: bool = True if input("can edit? (y/n): ").lower() == "y" else False
    with service_db:
        session = Session(bind=service_db)
        session.add(AdminModel(email=email, password=generate_password_hash(password), can_edit=can_edit))
        session.commit()
        print("Admin added")


def remove_admin():
    email: str = input("email: ")
    if input("Are you sure you want to delete this account? (y/n): ").lower() == "y":
        with service_db:
            session = Session(bind=service_db)
            admin = session.query(AdminModel).filter(AdminModel.email == email).all()
            if admin:
                session.query(admin).delete()
                session.commit()
                print("deleted")
            else:
                print("can't find admin with this email")
    else:
        print("canceled")


def create_tables():
    Base.metadata.create_all(service_db)
"""
