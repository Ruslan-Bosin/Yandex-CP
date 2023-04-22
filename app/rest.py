from config import SECRET_KEY
from app import app, logger
from app.models import ClientModel, OrganizationModel, RecordModel, AdminModel
from app.utils.token_required import token_required
from app.utils.validators import *
from flask import request, jsonify, make_response, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta, date
from uuid import uuid4
from sqlalchemy.orm import Session
from app.models import service_db


# Клиент
@app.route("/rest/client/login", methods=["POST"])
def rest_client_login():

    data: dict = request.get_json()
    email: str = data.get("email")
    password: str = data.get("password")

    if not email or not password:
        return make_response(jsonify({"message": "could not verify"}), 401)

    session = Session(bind=service_db)
    # client = ClientModel.get_or_none(ClientModel.email == email)
    client = session.query(ClientModel).filter(ClientModel.email == email).all()
    if not client:
        return make_response(jsonify({"message": "could not verify"}), 401)
    if not check_password_hash(client.password, password):
        return make_response(jsonify({"message": "could not verify"}), 401)

    token = jwt.encode({"role": "client", "id": client.id, "exp": datetime.utcnow() + timedelta(days=30)}, SECRET_KEY)

    return jsonify({"message": "successfully logged in", "token": token})


@app.route("/rest/client/signup", methods=["POST"])
def rest_client_signup():

    data: dict = request.get_json()
    name: str = data.get("name")
    email: str = data.get("email")
    password: str = data.get("password")

    if not name or not email or not password:
        return make_response(jsonify({"message": "parameters missing"}), 400)

    session = Session(bind=service_db)
    # email_taken = ClientModel.get_or_none(ClientModel.email == email)
    email_taken = session.query(ClientModel).filter(ClientModel.email == email).all()
    if email_taken:
        return make_response(jsonify({"message": "email taken"}), 417)

    if name_validator(name) is None and email_validator(email) is None and password_validator(password) is None:
        client_account = ClientModel(name=name, email=email, password=generate_password_hash(password))
        session.add(client_account)
        session.commit()
        # client_account.save()
    else:
        message = str()
        if password_validator(password):
            message = password_validator(password)
        if email_validator(email):
            message = email_validator(email)
        if name_validator(name):
            message = name_validator(name)
        return make_response(jsonify({"message": message}), 417)

    token = jwt.encode({"role": "client", "id": client_account.id, "exp": datetime.utcnow() + timedelta(days=30)}, SECRET_KEY)

    return jsonify({"message": "account created", "token": token})


@app.route("/rest/client/quick_signup", methods=["GET"])
def rest_client_quick_signup():
    session = Session(bind=service_db)
    client_account = ClientModel(
        name = "temp user",
        email = f"{uuid4()}@temp-user.coms",
        password = generate_password_hash("password"),
        is_private = True
    )
    # client_account.save()
    session.add(client_account)
    session.commit()

    token = jwt.encode({"role": "client", "id": client_account.id, "exp": datetime.utcnow() + timedelta(days=30)}, SECRET_KEY)

    return jsonify({"message": "successfully quick logged in", "token": token})


@app.route("/rest/client/active", methods=["GET"])
@token_required
def rest_client_active(rest_user):

    if not isinstance(rest_user, ClientModel):
        return make_response(jsonify({"message": "only the client has access"}), 401)

    session = Session(bind=service_db)
    # data = RecordModel.select().where(RecordModel.client == rest_user.id).order_by(RecordModel.accumulated.desc())
    data = session.query(RecordModel).filter(RecordModel.client == rest_user.id).order_by(RecordModel.accumulated.desc()).all()
    result = [{"image": url_for('organization_picture_get', id=item.organization.id),
               "title": item.organization.title,
               "accumulated": item.accumulated,
               "limit": item.organization.limit} for item in data]

    return jsonify(result)


@app.route("/rest/client/info", methods=["GET"])
@token_required
def rest_client_info(rest_user):

    if not isinstance(rest_user, ClientModel):
        return make_response(jsonify({"message": "only the client has access"}), 401)

    result = {
        "id": rest_user.id,
        "name": rest_user.name,
        "email": rest_user.email,
        "is_private": rest_user.is_private
    }

    return jsonify(result)


@app.route("/rest/client/info", methods=["PUT"])
@token_required
def rest_client_change(rest_user):

    if not isinstance(rest_user, ClientModel):
        return make_response(jsonify({"message": "only the client has access"}), 401)

    data: dict = request.get_json()
    name: str = data.get("name")
    email: str = data.get("email")
    password: str = data.get("password")
    is_private: bool = data.get("is_private")

    changed = list()
    session = Session(bind=service_db)
    if name is not None:
        if name_validator(name) is None:
            # client = ClientModel.get_or_none(ClientModel.id == rest_user.id)
            client = session.query(ClientModel).filter(ClientModel.id == rest_user.id).all()
            client.name = name
            # client.save()
            session.commit()
            changed.append("name")
        else:
            return make_response(jsonify({"message": f"name is not valid - {name_validator(name)}"}), 417)
    if email is not None:
        if email_validator(email) is None:
            # client = ClientModel.get_or_none(ClientModel.id == rest_user.id)
            client = session.query(ClientModel).filter(ClientModel.id == rest_user.id).all()
            client.email = email
            # client.save()
            changed.append("email")
        else:
            return make_response(jsonify({"message": f"email is not valid - {email_validator(email)}"}), 417)
    if password is not None:
        if password_validator(password) is None:
            # client = ClientModel.get_or_none(ClientModel.id == rest_user.id)
            client = session.query(ClientModel).filter(ClientModel.id == rest_user.id).all()
            client.password = generate_password_hash(password)
            # client.save()
            session.commit()
            changed.append("password")
        else:
            return make_response(jsonify({"message": f"password is not valid - {password_validator(password)}"}), 417)
    if is_private is not None:
        # client = ClientModel.get_or_none(ClientModel.id == rest_user.id)
        client = session.query(ClientModel).filter(ClientModel.id == rest_user.id).all()
        client.is_private = is_private
        # client.save()
        session.commit()
        changed.append("is_private")

    if changed:
        return jsonify({"message": f"{', '.join(changed)} updated"})

    return make_response(jsonify({"message": "nothing updated"}), 417)


# Организация
@app.route("/rest/organization/login", methods=["POST"])
def rest_organization_login():

    data: dict = request.get_json()
    email: str = data.get("email")
    password: str = data.get("password")

    if not email or not password:
        return make_response(jsonify({"message": "could not verify"}), 401)

    session = Session(bind=service_db)
    # organization = OrganizationModel.get_or_none(OrganizationModel.email == email)
    organization = session.query(OrganizationModel).filter(OrganizationModel.email == email).all()
    if not organization:
        return make_response(jsonify({"message": "could not verify"}), 401)
    if not check_password_hash(organization.password, password):
        return make_response(jsonify({"message": "could not verify"}), 401)

    token = jwt.encode({"role": "organization", "id": organization.id, "exp": datetime.utcnow() + timedelta(days=30)}, SECRET_KEY)

    return jsonify({"message": "successfully logged in", "token": token})


@app.route("/rest/organization/signup", methods=["POST"])
def rest_organization_signup():

    data: dict = request.get_json()
    title: str = data.get("title")
    email: str = data.get("email")
    password: str = data.get("password")

    if not title or not email or not password:
        return make_response(jsonify({"message": "parameters missing"}), 400)

    session = Session(bind=service_db)
    # email_taken = OrganizationModel.get_or_none(OrganizationModel.email == email)
    email_taken = session.query(OrganizationModel).filter(OrganizationModel.email == email).all()
    if email_taken:
        return make_response(jsonify({"message": "email taken"}), 417)

    if title_validator(title) is None and email_validator(email) is None and password_validator(password) is None:
        organization_account = OrganizationModel(title=title, email=email, password=generate_password_hash(password))
        session.add(organization_account)
        session.commit()
        # organization_account.save()
    else:
        message = str()
        if password_validator(password):
            message = password_validator(password)
        if email_validator(email):
            message = email_validator(email)
        if title_validator(title):
            message = title_validator(title)
        return make_response(jsonify({"message": message}), 417)

    token = jwt.encode({"role": "organization", "id": organization_account.id, "exp": datetime.utcnow() + timedelta(days=30)}, SECRET_KEY)

    return jsonify({"message": "account created", "token": token})


@app.route("/rest/organization/clients", methods=["GET"])
@token_required
def rest_organization_active(rest_user):

    if not isinstance(rest_user, OrganizationModel):
        return make_response(jsonify({"message": "only the organization has access"}), 401)

    session = Session(bind=service_db)
    # data = RecordModel.select().where(RecordModel.organization == rest_user.id).order_by(RecordModel.accumulated.desc())
    data = session.query(RecordModel).filter(RecordModel.organization == rest_user.id).order_by(RecordModel.accumulated.desc()).all()
    result = [{"name": item.client.name,
               "is_private": item.client.is_private,
               "accumulated": item.accumulated,
               "limit": item.organization.limit} for item in data]

    return jsonify(result)


@app.route("/rest/organization/info", methods=["GET"])
@token_required
def rest_organization_info(rest_user):

    if not isinstance(rest_user, OrganizationModel):
        return make_response(jsonify({"message": "only the organization has access"}), 401)

    result = {
        "id": rest_user.id,
        "title": rest_user.title,
        "email": rest_user.email,
        "sticker": rest_user.sticker,
        "limit": rest_user.limit,
        "image": url_for('organization_picture_get', id=rest_user.id) if rest_user.image else None,
    }

    return jsonify(result)


@app.route("/rest/organization/info", methods=["PUT"])
@token_required
def rest_organization_change(rest_user):

    if not isinstance(rest_user, OrganizationModel):
        return make_response(jsonify({"message": "only the organization has access"}), 401)

    data: dict = request.get_json()
    title: str = data.get("title")
    email: str = data.get("email")
    password: str = data.get("password")
    sticker: str = data.get("sticker")
    limit: int = data.get("limit")

    changed = list()
    session = Session(bind=service_db)
    if title is not None:
        if title_validator(title) is None:
            # organization = OrganizationModel.get_or_none(OrganizationModel.id == rest_user.id)
            organization = session.query(OrganizationModel).filter(OrganizationModel.id == rest_user.id).all()
            organization.title = title
            session.commit()
            # organization.save()
            changed.append("title")
        else:
            return make_response(jsonify({"message": f"title is not valid - {title_validator(title)}"}), 417)
    if email is not None:
        if email_validator(email) is None:
            # organization = OrganizationModel.get_or_none(OrganizationModel.id == rest_user.id)
            organization = session.query(OrganizationModel).filter(OrganizationModel.id == rest_user.id).all()
            organization.email = email
            # organization.save()
            session.commit()
            changed.append("email")
        else:
            return make_response(jsonify({"message": f"email is not valid - {email_validator(email)}"}), 417)
    if password is not None:
        if password_validator(password) is None:
            # organization = OrganizationModel.get_or_none(OrganizationModel.id == rest_user.id)
            organization = session.query(OrganizationModel).filter(OrganizationModel.id == rest_user.id).all()
            organization.password = generate_password_hash(password)
            # organization.save()
            session.commit()
            changed.append("password")
        else:
            return make_response(jsonify({"message": f"password is not valid - {password_validator(password)}"}), 417)
    if sticker is not None:
        if sticker_validator(sticker) is None:
            # organization = OrganizationModel.get_or_none(OrganizationModel.id == rest_user.id)
            organization = session.query(OrganizationModel).filter(OrganizationModel.id == rest_user.id).all()
            organization.sticker = sticker
            # organization.save()
            session.commit()
            changed.append("sticker")
        else:
            return make_response(jsonify({"message": f"sticker is not valid - {sticker_validator(sticker)}"}), 417)
    if limit is not None:
        if limit_validator(limit) is None:
            # organization = OrganizationModel.get_or_none(OrganizationModel.id == rest_user.id)
            organization = session.query(OrganizationModel).filter(OrganizationModel.id == rest_user.id).all()
            organization.limit = limit
            # organization.save()
            session.commit()
            changed.append("limit")
        else:
            return make_response(jsonify({"message": f"limit is not valid - {limit_validator(limit)}"}), 417)

    if changed:
        return jsonify({"message": f"{', '.join(changed)} updated"})

    return make_response(jsonify({"message": "nothing updated"}), 417)


@app.route("/rest/organization/upload", methods=["POST"])
@token_required
def rest_organization_change_picture_upload(rest_user):

    if not isinstance(rest_user, OrganizationModel):
        return make_response(jsonify({"message": "only the organization has access"}), 401)

    if "file" not in request.files:
        return make_response(jsonify({"message": "No file part in the request"}), 400)

    file = request.files['file']
    if file.filename == "":
        return make_response(jsonify({"message": "No file selected for uploading"}), 400)

    if file and image_validator(file.filename) is None:
        image = file.read()
        from sqlite3 import Binary  # TODO: change (remove sqlite3)
        bin_image = Binary(image)

        session = Session(bind=service_db)
        # organization = OrganizationModel.get(OrganizationModel.id == rest_user.id)
        organization = session.query(OrganizationModel).filter(OrganizationModel.id == rest_user.id).all()
        organization.image = bin_image
        # organization.save()
        session.commit()
        return jsonify({"message": "File successfully uploaded"})
    else:
        return make_response(jsonify({"message": f"{image_validator(file.filename)}"}), 400)


@app.route("/rest/organization/record", methods=["PUT"])
@token_required
def rest_organization_record(rest_user):

    if not isinstance(rest_user, OrganizationModel):
        return make_response(jsonify({"message": "only the organization has access"}), 401)

    data: dict = request.get_json()
    id: int = data.get("id")

    if not id:
        return make_response(jsonify({"message": "missing id"}), 400)

    session = Session(bind=service_db)
    # client_exists = ClientModel.get_or_none(ClientModel.id == id)
    client_exists = session.query(ClientModel).filter(ClientModel.id == id).all()

    if client_exists:
        # record_exists = RecordModel.get_or_none((RecordModel.client == id) & (RecordModel.organization == rest_user.id))
        record_exists = session.query(RecordModel).filter((RecordModel.client == id) &
                                                          (RecordModel.organization == rest_user.id)).all()

        if record_exists:
            record_exists.accumulated += 1
            record_exists.last_record_date = date.today()

            if record_exists.accumulated >= rest_user.limit:
                record_exists.accumulated = 0
                record_exists.save()
                return jsonify({"message": "accumulated"})

            record_exists.save()
            return jsonify({"message": "added"})
        else:
            # RecordModel(client=id, organization=rest_user.id, last_record_date=date.today()).save()
            session.add(RecordModel(client=id, organization=rest_user.id, last_record_date=date.today()))
            session.commit()
            return jsonify({"message": "record added"})
    else:
        return make_response(jsonify({"message": "wrong id"}), 417)


# Администрация
@app.route("/rest/admin/login", methods=["POST"])
def rest_admin_login():

    data: dict = request.get_json()
    email: str = data.get("email")
    password: str = data.get("password")

    if not email or not password:
        return make_response(jsonify({"message": "could not verify"}), 401)

    session = Session(bind=service_db)
    # admin = AdminModel.get_or_none(AdminModel.email == email)
    admin = session.query(AdminModel).filter(AdminModel.email == email).all()
    if not admin:
        return make_response(jsonify({"message": "could not verify"}), 401)
    if not check_password_hash(admin.password, password):
        return make_response(jsonify({"message": "could not verify"}), 401)

    token = jwt.encode({"role": "admin", "id": admin.id, "exp": datetime.utcnow() + timedelta(hours=12)}, SECRET_KEY)

    return jsonify({"message": "successfully logged in", "token": token})


@app.route("/rest/admin/clients", methods=["GET"])
@token_required
def rest_admin_clients(rest_user):

    if not isinstance(rest_user, AdminModel):
        return make_response(jsonify({"message": "no admin access"}), 401)

    data = ClientModel.select()
    result = list()
    for item in data:
        result.append({
            "id": item.id,
            "name": item.name,
            "email": item.email,
            "password": item.password,
            "is_private": item.is_private
        })

    return jsonify(result)


@app.route("/rest/admin/organizations", methods=["GET"])
@token_required
def rest_admin_organizations(rest_user):

    if not isinstance(rest_user, AdminModel):
        return make_response(jsonify({"message": "no admin access"}), 401)

    session = Session(bind=service_db)
    # data = OrganizationModel.select()
    data = session.query(OrganizationModel).all()
    result = list()
    for item in data:
        result.append({
            "id": item.id,
            "title": item.title,
            "email": item.email,
            "password": item.password,
            "limit": item.limit,
            "image": url_for('organization_picture_get', id=item.id) if item.image else None, #url_for('organization_picture_get', id=rest_user.id) if rest_user.image else None
            "sticker": item.sticker
        })

    return jsonify(result)


@app.route("/rest/admin/records", methods=["GET"])
@token_required
def rest_admin_records(rest_user):

    if not isinstance(rest_user, AdminModel):
        return make_response(jsonify({"message": "no admin access"}), 401)

    session = Session(bind=service_db)
    # data = RecordModel.select()
    data = session.query().all()
    result = list()

    for item in data:
        client_id = item.client_id
        organization_id = item.organization_id

        name = ClientModel.get_or_none(ClientModel.id == client_id)
        title = OrganizationModel.get_or_none(OrganizationModel.id == organization_id)

        result.append({
            "id": item.id,
            "client": client_id,
            "client_name": name.name if name else "удалено",
            "organization": organization_id,
            "organization_title": title.title if title else "удалено",
            "accumulated": item.accumulated,
            "last_record_date": item.last_record_date
            })

    return jsonify(result)


@app.route("/rest/admin/info", methods=["GET"])
@token_required
def rest_admin_info(rest_user):

    if not isinstance(rest_user, AdminModel):
        return make_response(jsonify({"message": "no admin access"}), 401)

    result = {
        "id": rest_user.id,
        "email": rest_user.email,
        "password": rest_user.password,
        "can_edit": rest_user.can_edit
    }

    return jsonify(result)


# Создание записи
@app.route("/rest/admin/create/record", methods=["POST"])
@token_required
def rest_admin_create_record(rest_user):

    if not isinstance(rest_user, AdminModel):
        return make_response(jsonify({"message": "no admin access"}), 401)

    data: dict = request.get_json()
    client_id: str = data.get("client_id")
    organization_id: str = data.get("organization_id")

    if not client_id or not organization_id:
        return make_response(jsonify({"message": "arguments missing"}), 400)

    session = Session(bind=service_db)
    # client_exists = ClientModel.get_or_none(ClientModel.id == int(client_id))
    client_exists = session.query(ClientModel).filter(ClientModel.id == int(client_id)).all()
    # organization_exists = OrganizationModel.get_or_none(OrganizationModel.id == int(organization_id))
    organization_exists = session.query(OrganizationModel).filter(OrganizationModel.id == int(organization_id)).all()

    if not client_exists or not organization_exists:
        return make_response(jsonify({"message": "bad arguments"}), 400)

    # record_exists = RecordModel.get_or_none((RecordModel.client == int(client_id)) & (RecordModel.organization == int(organization_id)))
    record_exists = session.query(RecordModel).filter((RecordModel.client == int(client_id)) &
                                                      (RecordModel.organization == int(organization_id))).all()
    if record_exists:
        return make_response(jsonify({"message": "record exists"}), 400)

    # RecordModel(client=int(client_id), organization=int(organization_id), last_record_date=date.today()).save()
    session.add(RecordModel(client=int(client_id), organization=int(organization_id), last_record_date=date.today()))
    session.commit()

    return jsonify({"message": "record created"})


@app.route("/rest/admin/clients/update", methods=["PUT"])
@token_required
def rest_admin_clients_update(rest_user):

    if not isinstance(rest_user, AdminModel):
        return make_response(jsonify({"message": "no admin access"}), 401)

    data: dict = request.get_json()
    client_id: str = data.get("id")
    name: str = data.get("name")
    email: str = data.get("email")
    password: str = data.get("password")
    is_private: bool = data.get("is_private")

    if not client_id:
        return make_response(jsonify({"message": "arguments missing"}), 400)

    session = Session(bind=service_db)
    changed = list()
    if name is not None:
        if name_validator(name) is None:
            # client = ClientModel.get_or_none(ClientModel.id == client_id)
            client = session.query(ClientModel).filter(ClientModel.id == client_id).all()
            client.name = name
            # client.save()
            session.commit()
            changed.append("name")
        else:
            return make_response(jsonify({"message": f"name is not valid - {name_validator(name)}"}), 417)
    if email is not None:
        if email_validator(email) is None:
            # client = ClientModel.get_or_none(ClientModel.id == client_id)
            client = session.query(ClientModel).filter(ClientModel.id == client_id).all()
            client.email = email
            # client.save()
            session.commit()
            changed.append("email")
        else:
            return make_response(jsonify({"message": f"email is not valid - {email_validator(email)}"}), 417)
    if password is not None:
        if password_validator(password) is None:
            # client = ClientModel.get_or_none(ClientModel.id == client_id)
            client = session.query(ClientModel).filter(ClientModel.id == client_id).all()
            client.password = generate_password_hash(password)
            # client.save()
            session.commit()
            changed.append("password")
        else:
            return make_response(jsonify({"message": f"password is not valid - {password_validator(password)}"}), 417)
    if is_private is not None:
        # client = ClientModel.get_or_none(ClientModel.id == client_id)
        client = session.query(ClientModel).filter(ClientModel.id == client_id).all()
        client.is_private = is_private
        # client.save()
        session.commit()
        changed.append("is_private")

    if changed:
        return jsonify({"message": f"{', '.join(changed)} updated"})

    return make_response(jsonify({"message": "nothing updated"}), 417)


@app.route("/rest/admin/clients/remove", methods=["POST"])
@token_required
def rest_admin_clients_remove(rest_user):

    if not isinstance(rest_user, AdminModel):
        return make_response(jsonify({"message": "no admin access"}), 401)

    data: dict = request.get_json()
    client_id: str = data.get("id")

    if not client_id:
        return make_response(jsonify({"message": "arguments missing"}), 400)

    session = Session(bind=service_db)
    # client_exists = ClientModel.get_or_none(ClientModel.id == client_id)
    client_exists = session.query(ClientModel).filter(ClientModel.id == client_id).all()
    if not client_exists:
        return make_response(jsonify({"message": "no such client"}), 400)
    client_exists.delete_instance()

    return jsonify({"message": "client removed"})


@app.route("/rest/admin/organizations/update", methods=["PUT"])
@token_required
def rest_admin_organizations_update(rest_user):

    if not isinstance(rest_user, AdminModel):
        return make_response(jsonify({"message": "no admin access"}), 401)

    data: dict = request.get_json()
    organization_id: str = data.get("id")
    title: str = data.get("title")
    email: str = data.get("email")
    password: str = data.get("password")
    sticker: str = data.get("sticker")
    limit: int = data.get("limit")

    if not organization_id:
        return make_response(jsonify({"message": "arguments missing"}), 400)

    changed = list()
    session = Session(bind=service_db)
    if title is not None:
        if title_validator(title) is None:
            # organization = OrganizationModel.get_or_none(OrganizationModel.id == organization_id)
            organization = session.query(OrganizationModel).filter(OrganizationModel.id == organization_id).all()
            organization.title = title
            # organization.save()
            session.commit()
            changed.append("title")
        else:
            return make_response(jsonify({"message": f"title is not valid - {title_validator(title)}"}), 417)
    if email is not None:
        if email_validator(email) is None:
            # TODO: проверка на уникальность email-а
            # organization = OrganizationModel.get_or_none(OrganizationModel.id == organization_id)
            organization = session.query(OrganizationModel).filter(OrganizationModel.id == organization_id).all()
            organization.email = email
            # organization.save()
            session.commit()
            changed.append("email")
        else:
            return make_response(jsonify({"message": f"email is not valid - {email_validator(email)}"}), 417)
    if password is not None:
        if password_validator(password) is None:
            # organization = OrganizationModel.get_or_none(OrganizationModel.id == organization_id)
            organization = session.query(OrganizationModel).filter(OrganizationModel.id == organization_id).all()
            organization.password = generate_password_hash(password)
            # organization.save()
            session.commit()
            changed.append("password")
        else:
            return make_response(jsonify({"message": f"password is not valid - {password_validator(password)}"}), 417)
    if sticker is not None:
        if sticker_validator(sticker) is None:
            # organization = OrganizationModel.get_or_none(OrganizationModel.id == organization_id)
            organization = session.query(OrganizationModel).filter(OrganizationModel.id == organization_id).all()
            organization.sticker = sticker
            # organization.save()
            session.commit()
            changed.append("sticker")
        else:
            return make_response(jsonify({"message": f"sticker is not valid - {sticker_validator(sticker)}"}), 417)
    if limit is not None:
        if limit_validator(limit) is None:
            # organization = OrganizationModel.get_or_none(OrganizationModel.id == organization_id)
            organization = session.query(OrganizationModel).filter(OrganizationModel.id == organization_id).all()
            organization.limit = limit
            # organization.save()
            session.commit()
            changed.append("limit")
        else:
            return make_response(jsonify({"message": f"limit is not valid - {limit_validator(limit)}"}), 417)

    if changed:
        return jsonify({"message": f"{', '.join(changed)} updated"})

    return make_response(jsonify({"message": "nothing updated"}), 417)


@app.route("/rest/admin/organizations/remove", methods=["POST"])
@token_required
def rest_admin_organizations_remove(rest_user):

    if not isinstance(rest_user, AdminModel):
        return make_response(jsonify({"message": "no admin access"}), 401)

    data: dict = request.get_json()
    organization_id: str = data.get("id")

    if not organization_id:
        return make_response(jsonify({"message": "arguments missing"}), 400)
    session = Session(bind=service_db)
    # organization_exists = OrganizationModel.get_or_none(OrganizationModel.id == organization_id)
    organization_exists = session.query(OrganizationModel).filter(OrganizationModel.id == organization_id).all()
    if not organization_exists:
        return make_response(jsonify({"message": "no such client"}), 400)
    organization_exists.delete_instance()

    return jsonify({"message": "organization removed"})


@app.route("/rest/admin/records/update", methods=["PUT"])
@token_required
def rest_admin_records_update(rest_user):

    if not isinstance(rest_user, AdminModel):
        return make_response(jsonify({"message": "no admin access"}), 401)

    data: dict = request.get_json()
    record_id: str = data.get("id")
    accumulated: int = data.get("accumulated")
    last_record_date: str = data.get("last_record_date")

    if not record_id:
        return make_response(jsonify({"message": "arguments missing"}), 400)

    changed = list()
    session = Session(bind=service_db)
    if accumulated is not None:
        # record = RecordModel.get_or_none(RecordModel.id == record_id)
        record = session.query(RecordModel).filter(RecordModel.id == record_id).all()
        record.accumulated = accumulated
        # record.save()
        session.commit()
        changed.append("accumulated")
    if last_record_date is not None:
        try:
            day, month, year = map(int, last_record_date.split("."))
            # record = RecordModel.get_or_none(RecordModel.id == record_id)
            record = session.query(RecordModel).filter(RecordModel.id == record_id).all()
            record.last_record_date = date(year=year, month=month, day=day)
            # record.save()
            session.commit()
            changed.append("last_record_date")
        except:
            return make_response(jsonify({"message": "bad date arguments"}), 400)

    if changed:
        return jsonify({"message": f"{', '.join(changed)} updated"})

    return make_response(jsonify({"message": "nothing updated"}), 417)


@app.route("/rest/admin/records/remove", methods=["POST"])
@token_required
def rest_admin_records_remove(rest_user):

    if not isinstance(rest_user, AdminModel):
        return make_response(jsonify({"message": "no admin access"}), 401)

    data: dict = request.get_json()
    record_id: str = data.get("id")

    if not record_id:
        return make_response(jsonify({"message": "arguments missing"}), 400)

    session = Session(bind=service_db)
    # record_exists = RecordModel.get_or_none(RecordModel.id == record_id)
    record_exists = session.query(RecordModel).filter(RecordModel.id == record_id).all()
    if not record_exists:
        return make_response(jsonify({"message": "no such record"}), 400)
    record_exists.delete_instance()

    return jsonify({"message": "record removed"})


# Проверка админ token-а
@app.route("/rest/admin/verify_token", methods=["GET"])
@token_required
def rest_admin_verify_token(rest_user):

    if not isinstance(rest_user, AdminModel):
        return make_response(jsonify({"message": "no admin access"}), 401)

    return jsonify({"message": "token is valid"})


# Адрес для выяснения включен ли сервер
@app.route("/rest/is_server_on", methods=["GET"])
def rest_is_server_on():
    return jsonify({"message": "server is on"})
