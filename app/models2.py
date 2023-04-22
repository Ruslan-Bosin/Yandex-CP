from peewee import Model
from peewee import AutoField, CharField, BooleanField, IntegerField, BlobField, ForeignKeyField, DateField, \
    FixedCharField
from app import service_db
from werkzeug.security import generate_password_hash


class BaseModel(Model):
    class Meta:
        database = service_db


class ClientModel(BaseModel):
    id = AutoField(null=False, primary_key=True)
    name = CharField(null=False)
    email = CharField(null=False, unique=True)
    password = CharField(null=False)
    is_private = BooleanField(default=False)

    class Meta:
        db_table = "clients"

    def to_dict(self):
        return self.__data__


class OrganizationModel(BaseModel):
    id = AutoField(null=False, primary_key=True)
    title = CharField(null=False)
    email = CharField(null=False, unique=True)
    password = CharField(null=False)
    limit = IntegerField(default=10)
    image = BlobField(default='')
    sticker = FixedCharField(max_length=1, null=False, default="⭐")

    class Meta:
        db_table = "organizations"

    def to_dict(self):
        return self.__data__


class RecordModel(BaseModel):
    id = AutoField(null=False, primary_key=True)
    client = ForeignKeyField(ClientModel, null=False)
    organization = ForeignKeyField(OrganizationModel, null=False)
    accumulated = IntegerField(null=False, default=1)
    last_record_date = DateField(null=False)

    class Meta:
        db_table = "records"

    def to_dict(self):
        return self.__data__


class AdminModel(BaseModel):
    id = AutoField(null=False, primary_key=True)
    email = CharField(null=False, unique=True)
    password = CharField(null=False)
    can_edit = BooleanField(null=False)

    class Meta:
        db_table = "admins"

    def to_dict(self):
        return self.__data__


def create_table():
    with service_db:
        service_db.create_tables([ClientModel, OrganizationModel, RecordModel, AdminModel])


def add_admin():
    email: str = input("email: ")
    password: str = input("password: ")
    can_edit: bool = True if input("can edit? (y/n): ").lower() == "y" else False
    with service_db:
        AdminModel(email=email, password=generate_password_hash(password), can_edit=can_edit).save()
        print("Admin added")


def remove_admin():
    email: str = input("email: ")
    if input("Are you sure you want to delete this account? (y/n): ").lower() == "y":
        with service_db:
            admin = AdminModel.get_or_none(AdminModel.email == email)
            if admin:
                admin.delete_instance()
                print("deleted")
            else:
                print("can't find admin with this email")
    else:
        print("canceled")
