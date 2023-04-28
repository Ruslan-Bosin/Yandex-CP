from app import logger, login_manager

"""
from app.models import ClientModel, OrganizationModel
from sqlalchemy.orm import Session
from app.models import service_db
"""

from app import db
from app.models import ClientModel, OrganizationModel, RecordModel

# TODO: Обработку ошибок добавить

class User:

    _user = None
    _role = None

    def create_with_user_id(self, user_id: str):
        if user_id.startswith("c"):
            # self._user = ClientModel.get(ClientModel.id == int(user_id[1::]))
            self._user = db.session.query(ClientModel).filter(ClientModel.id == int(user_id[1::])).first()
            self._role = "client"
        elif user_id.startswith("o"):
            # self._user = OrganizationModel.get(OrganizationModel.id == int(user_id[1::]))
            # self._user = session.query(OrganizationModel).get(OrganizationModel.id == int(user_id[1::]))
            self._user = db.session.query(OrganizationModel).filter(OrganizationModel.id == int(user_id[1::])).first()
            self._role = "organization"
        else:
            logger.error(f"Неизвестный префикс user_id: {user_id}")
        return self

    def create_with_client_user(self, user):
        self._user = user
        self._role = "client"
        return self

    def create_with_organization_user(self, user):
        self._user = user
        self._role = "organization"
        return self

    def is_client(self):
        if self._role == "client":
            return True
        else:
            return False

    def is_organization(self):
        if self._role == "organization":
            return True
        else:
            return False

    def get_id(self):
        if self._role == "client":
            return f"c{self._user.id}"
        elif self._role == "organization":
            return f"o{self._user.id}"

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def is_active(self):
        return True

    def get_role(self):
        return self._role


@login_manager.user_loader
def load_user(user_id: str):
    return User().create_with_user_id(user_id=user_id)
