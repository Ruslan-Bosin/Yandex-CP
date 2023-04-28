from functools import wraps
from config import SECRET_KEY
from flask import request, jsonify, make_response

import jwt

from app import db
from app.models import ClientModel, OrganizationModel, RecordModel,AdminModel



def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "x-access-token" in request.headers:
            token = request.headers["x-access-token"]

        if token is None:
            return make_response(jsonify({"message": "token is missing"}), 401)

        try:
            rest_user = None
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            role = data["role"]
            if role == "client":
                try:
                    rest_user = db.session.query(ClientModel).filter(ClientModel.id == data["id"]).all()[0]
                except:
                    rest_user = None
            elif role == "organization":
                try:
                    rest_user = db.session.query(ClientModel).filter(OrganizationModel.id == data["id"]).all()[0]
                except:
                    rest_user = None
            elif role == "admin":
                try:
                    rest_user = db.session.query(ClientModel).filter(AdminModel.get_or_none(AdminModel.id == data["id"])).all()[0]
                except:
                    rest_user = None
        except Exception as error:
            return make_response(jsonify({"message": "token is missing (error)"}), 401)

        return f(rest_user, *args, **kwargs)

    return decorated
