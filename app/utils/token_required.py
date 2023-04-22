from functools import wraps
from config import SECRET_KEY
from flask import request, jsonify, make_response
from app.models import ClientModel, OrganizationModel, AdminModel
import jwt


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "x-access-token" in request.headers:
            token = request.headers["x-access-token"]

        if not token:
            return make_response(jsonify({"message": "token is missing"}), 401)

        try:
            rest_user = None
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            role = data["role"]
            if role == "client":
                rest_user = ClientModel.get_or_none(ClientModel.id == data["id"])
            elif role == "organization":
                rest_user = OrganizationModel.get_or_none(OrganizationModel.id == data["id"])
            elif role == "admin":
                rest_user = AdminModel.get_or_none(AdminModel.id == data["id"])
        except Exception as error:
            return make_response(jsonify({"message": "token is missing"}), 401)

        return f(rest_user, *args, **kwargs)

    return decorated
