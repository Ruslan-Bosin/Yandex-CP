from config import SERVICE_DATABASE
from sqlalchemy import Column, ForeignKey, Boolean, String, Integer, LargeBinary, Date
from werkzeug.security import generate_password_hash
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, Session
from sqlalchemy_serializer import SerializerMixin


service_db = create_engine(f'sqlite:///{SERVICE_DATABASE}?check_same_thread=False', echo=True)
Base = declarative_base()


class ClientModel(Base, SerializerMixin):
    __tablename__ = 'clients'

    id = Column(Integer, nullable=False, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    is_private = Column(Boolean, default=False)
    Record = relationship('RecordModel')


class OrganizationModel(Base, SerializerMixin):
    __tablename__ = 'organizations'

    id = Column(Integer, nullable=False, primary_key=True)
    title = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    limit = Column(Integer, default=10)
    image = Column(LargeBinary, default=b'')
    sticker = Column(String(1), nullable=False, default="⭐")
    Record = relationship('RecordModel')

    def to_dict(self):
        return {"id": self.id, "title": self.title, "email": self.email, "limit": self.limit, "image": self.image, "sticker": self.sticker, "Record": self.Record}


class RecordModel(Base, SerializerMixin):
    __tablename__ = 'records'

    id = Column(Integer, nullable=False, primary_key=True)
    client = Column(Integer, ForeignKey('clients.id'), nullable=False)
    organization = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    accumulated = Column(Integer, nullable=False, default=1)
    last_record_date = Column(Date, nullable=False)
    Organization = relationship('OrganizationModel')
    Client = relationship('ClientModel')


class AdminModel(Base, SerializerMixin):
    __tablename__ = 'admins'

    id = Column(Integer, nullable=False, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    can_edit = Column(Boolean, nullable=False)


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
