from app import app, logger
from flask import render_template, url_for, flash, redirect, abort, make_response, request
from app.forms import ClientLoginForm, ClientSignupForm, OrganizationLoginForm, OrganizationSignupForm, NewRecordForm,\
    ClientChangeName, ClientChangeEmail, ClientChangePassword, OrganizationChangeName, OrganizationChangeEmail, \
    OrganizationChangePassword, OrganizationChangeSticker, OrganizationChangeLimit
from app.utils.validators import name_validator, email_validator, password_validator, password_confirmation_validator, \
    title_validator, sticker_validator, image_validator, limit_validator
from app.models import ClientModel, OrganizationModel, RecordModel
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from app.utils.template_filters import style, script
from flask_login import login_user, login_required, current_user, logout_user
from app.login import User
from sqlalchemy.orm import Session
from app.models import service_db


# Отслеживание URL
# Ознакомительная страница
@logger.catch
@app.route("/")
def index() -> str:

    return redirect("select_role")

    data: [str, object] = {
        "title": "Главная страница",
        "start_url": url_for("select_role"),
        "ui_kit_styles_url": url_for("static", filename="css/ui_kit_styles.css"),
        "index_styles_url": url_for("static", filename="css/index_styles.css"),
        "index_script_url": url_for("static", filename="js/index_script.js"),
    }

    if isinstance(current_user, User):
        if current_user.is_client():
            data["start_url"] = url_for("client")
        elif current_user.is_organization():
            data["start_url"] = url_for("organization")

    return render_template("index.html", **data)


# Выбор роли: клиент / организация
@logger.catch
@app.route("/select_role")
def select_role() -> str:
    data_html: [str, object] = {
        "title": "Выберите кто вы",
        "index_url": url_for("index"),
        "client_login_url": url_for("client_login"),
        "organization_login_url": url_for("organization_login"),
        "ui_kit_styles_url": url_for("static", filename="css/ui_kit_styles.css"),
        "select_role_styles_url": url_for("static", filename="css/select_role_styles.css"),
        "select_role_script_url": url_for("static", filename="js/select_role_script.js"),
    }
    return render_template("select_role.html", **data_html)


# Клиент - выход
@logger.catch
@login_required
@app.route("/client/logout", methods=["POST", "GET"])
def client_logout():

    if current_user.is_organization():
        abort(401)

    logout_user()

    return redirect(url_for("select_role"))

# Клиент - вход
@logger.catch
@app.route("/client/login", methods=["POST", "GET"])
def client_login():
    form = ClientLoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        if email_validator(email) is None and password_validator(password) is None:
            # client_account = ClientModel.get_or_none(ClientModel.email == email)
            session = Session(bind=service_db)
            client_account = session.query(ClientModel).filter(ClientModel.email == email).first()
            if client_account and check_password_hash(client_account.password, password):
                user = User().create_with_client_user(user=client_account)
                login_user(user)
                return redirect(url_for("client"))
            else:
                flash("неверный логи и/или пароль")
        else:
            flash_message = str()
            if password_validator(password):
                flash_message = password_validator(password)
            if email_validator(email):
                flash_message = email_validator(email)
            flash(flash_message)

    data: [str, object] = {
        "title": "Вход - клиент",
        "select_role_url": url_for("select_role"),
        "client_signup_url": url_for("client_signup"),
        "ui_kit_styles_url": url_for("static", filename="css/ui_kit_styles.css"),
        "client_login_styles_url": url_for("static", filename="css/client_login_styles.css"),
        "client_login_script_url": url_for("static", filename="js/client_login_script.js"),
        "form": form,
        "data_css": {
            "url_for": url_for
        }
    }
    return render_template("client_login.html", **data)


# Клиент - регистрация
@logger.catch
@app.route("/client/signup", methods=["POST", "GET"])
def client_signup():

    form = ClientSignupForm()

    if form.validate_on_submit():
        name = form.name.data.capitalize()
        email = form.email.data.lower()
        password = form.password.data
        password_confirmation = form.password_confirmation.data

        if name_validator(name) is None and email_validator(email) is None and \
                password_validator(password) is None and \
                password_confirmation_validator(password, password_confirmation) is None:
            # email_taken = ClientModel.get_or_none(ClientModel.email == email)
            session = Session(bind=service_db)
            email_taken = session.query(ClientModel).filter(ClientModel.email == email).all()
            if email_taken:
                flash("Данный email уже занят")
            else:
                client_account = ClientModel(name=name, email=email, password=generate_password_hash(password))
                session.add(client_account)
                session.commit()
                # client_account.save()
                user = User().create_with_client_user(user=client_account)
                login_user(user)
                return redirect(url_for("client"))
        else:
            flash_message = str()
            if password_confirmation_validator(password, password_confirmation):
                flash_message = password_confirmation_validator(password, password_confirmation)
            if password_validator(password):
                flash_message = password_validator(password)
            if email_validator(email):
                flash_message = email_validator(email)
            if name_validator(name):
                flash_message = name_validator(name)
            flash(flash_message)

    data: [str, object] = {
        "title": "Регистрация - клиент",
        "select_role_url": url_for("select_role"),
        "client_login_url": url_for("client_login"),
        "ui_kit_styles_url": url_for("static", filename="css/ui_kit_styles.css"),
        "client_signup_styles_url": url_for("static", filename="css/client_signup_styles.css"),
        "client_signup_script_url": url_for("static", filename="js/client_signup_script.js"),
        "form": form,
        "data_css": {
            "url_for": url_for
        }
    }
    return render_template("client_signup.html", **data)


# Основная страница - клиент
@logger.catch
@app.route("/client")
@login_required
def client() -> str:
    session = Session(bind=service_db)
    if current_user.is_organization():
        abort(401)
    print(current_user._user)
    data: [str, object] = {
        "title": "Клиент",
        "ui_kit_styles_url": url_for("static", filename="css/ui_kit_styles.css"),
        "client_styles_url": url_for("static", filename="css/client_styles.css"),
        "client_script_url": url_for("static", filename="js/client_script.js"),
        "client_settings_url": url_for("client_settings"),
        # "active": sorted(RecordModel.select().where(RecordModel.client == int(current_user._user.id)).order_by(RecordModel.accumulated), key=lambda item: item.accumulated / OrganizationModel.select().where(OrganizationModel.id == item.organization)[0].limit, reverse=True),
        "active": sorted(session.query(RecordModel).filter(RecordModel.client == int(current_user._user.id)).order_by(RecordModel.accumulated).all(), key=lambda item: item.accumulated / session.query(OrganizationModel).filter(OrganizationModel.id == item.organization).first().limit, reverse=True),
        "user_id": current_user._user.to_dict()["id"],
        "str": str,
        "data_js": {
            "user_id": current_user._user.to_dict()["id"]
        }
    }
    return render_template("client.html", **data)


# Основные настройки - клиент
@logger.catch
@app.route("/client/settings")
@login_required
def client_settings() -> str:

    if current_user.is_organization():
        abort(401)

    data: [str, object] = {
        "title": "Настройки",
        "ui_kit_styles_url": url_for("static", filename="css/ui_kit_styles.css"),
        "client_settings_styles_url": url_for("static", filename="css/client_settings_styles.css"),
        "client_settings_script_url": url_for("static", filename="js/client_settings_script.js"),
        "client_main_url": url_for("client"),
        "client_logout_url": url_for("client_logout"),
        "client_settings_change_name_url": url_for("client_settings_change_name"),
        "client_settings_change_email_url": url_for("client_settings_change_email"),
        "client_settings_change_privacy_url": url_for("client_settings_change_privacy"),
        "client_settings_change_password_url": url_for("client_settings_change_password"),
        "user_info": current_user._user.to_dict(),
        "data_css": {
            "url_for": url_for
        }
    }
    return render_template("client_settings.html", **data)


# Основные настройки - клиент, сменя имени
@logger.catch
@app.route("/client/settings/change_name", methods=["POST", "GET"])
@login_required
def client_settings_change_name():

    if current_user.is_organization():
        abort(401)

    form = ClientChangeName()

    if form.validate_on_submit():
        name = form.name.data

        if name_validator(name) is None:
            session = Session(bind=service_db)
            # client_account = ClientModel.get(ClientModel.id == current_user._user.id)
            client_account = session.query(ClientModel).filter(ClientModel.id == current_user._user.id).first()
            client_account.name = name
            session.commit()
            current_user._user.name = name
            return redirect(url_for("client_settings"))
        else:
            flash_message = str()
            if name_validator(name):
                flash_message = name_validator(name)
            flash(flash_message)

    data: [str, object] = {
        "title": "Сменить имя",
        "ui_kit_styles_url": url_for("static", filename="css/ui_kit_styles.css"),
        "client_settings_change_name_styles_url": url_for("static", filename="css/client_settings_change_name_styles.css"),
        "client_settings_change_name_script_url": url_for("static", filename="js/client_settings_change_name_script.js"),
        "form": form,
        "client_settings_url": url_for("client_settings"),
        "data_css": {
            "url_for": url_for
        },
        "data_js": {
            "user_info": current_user._user.to_dict()
        }
    }

    return render_template("client_settings_change_name.html", **data)


# Основные настройки - клиент, сменя почты
@logger.catch
@app.route("/client/settings/change_email", methods=["POST", "GET"])
@login_required
def client_settings_change_email():

    if current_user.is_organization():
        abort(401)

    form = ClientChangeEmail()

    if form.validate_on_submit():
        email = form.email.data

        if email_validator(email) is None:
            session = Session(bind=service_db)
            # client_account = ClientModel.get(ClientModel.id == current_user._user.id)
            client_account = session.query(ClientModel).filter(ClientModel.id == current_user._user.id).first()
            client_account.email = email
            session.commit()
            current_user._user.email = email
            return redirect(url_for("client_settings"))
        else:
            flash_message = str()
            if email_validator(email):
                flash_message = email_validator(email)
            flash(flash_message)

    data: [str, object] = {
        "title": "Сменить email",
        "ui_kit_styles_url": url_for("static", filename="css/ui_kit_styles.css"),
        "client_settings_change_email_styles_url": url_for("static", filename="css/client_settings_change_email_styles.css"),
        "client_settings_change_email_script_url": url_for("static", filename="js/client_settings_change_email_script.js"),
        "form": form,
        "client_settings_url": url_for("client_settings"),
        "data_js": {
            "user_info": current_user._user.to_dict()
        },
        "data_css": {
            "url_for": url_for
        }
    }

    return render_template("client_settings_change_email.html", **data)


# Основные настройки - клиент, сменя пароля
@logger.catch
@app.route("/client/settings/change_password", methods=["POST", "GET"])
@login_required
def client_settings_change_password():

    if current_user.is_organization():
        abort(401)

    form = ClientChangePassword()

    if form.validate_on_submit():
        password = form.password.data
        session = Session(bind=service_db)
        if password_validator(password) is None:
            # client_account = ClientModel.get(ClientModel.id == current_user._user.id)
            client_account = session.query(ClientModel).filter(ClientModel.id == current_user._user.id).first()
            client_account.password = generate_password_hash(password)
            # client_account.save()
            session.commit()
            current_user._user.password = generate_password_hash(password)
            return redirect(url_for("client_settings"))
        else:
            flash_message = str()
            if password_validator(password):
                flash_message = password_validator(password)
            flash(flash_message)

    data: [str, object] = {
        "title": "Сменить пароль",
        "ui_kit_styles_url": url_for("static", filename="css/ui_kit_styles.css"),
        "client_settings_change_password_styles_url": url_for("static", filename="css/client_settings_change_password_styles.css"),
        "client_settings_change_password_script_url": url_for("static", filename="js/client_settings_change_password_script.js"),
        "form": form,
        "client_settings_url": url_for("client_settings"),
        "data_css": {
            "url_for": url_for
        }
    }

    return render_template("client_settings_change_password.html", **data)


# Основные настройки - клиент, сменя настройки приватности
@logger.catch
@app.route("/client/settings/change_privacy", methods=["POST", "GET"])
@login_required
def client_settings_change_privacy():

    if current_user.is_organization():
        abort(401)

    data: [str, object] = {
        "title": "Сменить Настройки приватности",
        "ui_kit_styles_url": url_for("static", filename="css/ui_kit_styles.css"),
        "client_settings_change_privacy_styles_url": url_for("static", filename="css/client_settings_change_privacy_styles.css"),
        "client_settings_change_privacy_script_url": url_for("static", filename="js/client_settings_change_privacy_script.js"),
        "client_settings_change_privacy_to_standard_url": url_for("client_settings_change_privacy_to_standard"),
        "client_settings_change_privacy_to_private_url": url_for("client_settings_change_privacy_to_private"),
        "client_settings_url": url_for("client_settings"),
        "data_js": {
            "user_info": current_user._user.to_dict()
        }
    }

    return render_template("client_settings_change_privacy.html", **data)


# Основные настройки - клиент, сменя настройки приватности - стандартный
@logger.catch
@app.route("/client/settings/change_privacy/to_standard", methods=["POST", "GET"])
@login_required
def client_settings_change_privacy_to_standard():

    if current_user.is_organization():
        abort(401)

    session = Session(bind=service_db)
    # client_account = ClientModel.get(ClientModel.id == current_user._user.id)
    client_account = session.query(ClientModel).filter(ClientModel.id == current_user._user.id).first()
    client_account.is_private = False
    # client_account.save()
    session.commit()
    current_user._user.is_private = False

    return redirect(url_for("client_settings"))


# Основные настройки - клиент, сменя настройки приватности - приватный
@logger.catch
@app.route("/client/settings/change_privacy/to_private", methods=["POST", "GET"])
@login_required
def client_settings_change_privacy_to_private():

    if current_user.is_organization():
        abort(401)

    session = Session(bind=service_db)
    # client_account = ClientModel.get(ClientModel.id == current_user._user.id)
    client_account = session.query(ClientModel).filter(ClientModel.id == current_user._user.id).first()
    client_account.is_private = True
    # client_account.save()
    session.commit()
    current_user._user.is_private = True

    return redirect(url_for("client_settings"))


# Организация - выход
@logger.catch
@login_required
@app.route("/organization/logout", methods=["POST", "GET"])
def organization_logout():

    if current_user.is_client():
        abort(401)

    logout_user()

    return redirect(url_for("select_role"))


# Организация - вход
@logger.catch
@app.route("/organization/login", methods=["POST", "GET"])
def organization_login():
    form = OrganizationLoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        if email_validator(email) is None and password_validator(password) is None:
            session = Session(bind=service_db)
            # organization_account = OrganizationModel.get_or_none(OrganizationModel.email == email)
            organization_account = session.query(OrganizationModel).filter(OrganizationModel.email == email).first()
            if organization_account and check_password_hash(organization_account.password, password):
                user = User().create_with_organization_user(user=organization_account)
                login_user(user)
                return redirect(url_for("organization"))
            else:
                flash("неверный логи и/или пароль")
        else:
            flash_message = str()
            if password_validator(password):
                flash_message = password_validator(password)
            if email_validator(email):
                flash_message = email_validator(email)
            flash(flash_message)

    data: [str, object] = {
        "title": "Вход - организация",
        "select_role_url": url_for("select_role"),
        "organization_signup_url": url_for("organization_signup"),
        "ui_kit_styles_url": url_for("static", filename="css/ui_kit_styles.css"),
        "organization_login_styles_url": url_for("static", filename="css/organization_login_styles.css"),
        "organization_login_script_url": url_for("static", filename="js/organization_login_script.js"),
        "form": form,
        "data_css": {
            "url_for": url_for
        }
    }
    return render_template("organization_login.html", **data)


# Организация - регистрация
@logger.catch
@app.route("/organization/signup", methods=["POST", "GET"])
def organization_signup():
    form = OrganizationSignupForm()

    if form.validate_on_submit():
        title = (form.title.data).capitalize()
        email = (form.email.data).lower()
        password = form.password.data
        password_confirmation = form.password_confirmation.data

        if name_validator(title) is None and email_validator(email) is None and password_validator(password) is None \
                and password_confirmation_validator(password, password_confirmation) is None:
            session = Session(bind=service_db)
            # email_taken = OrganizationModel.get_or_none(OrganizationModel.email == email)
            email_taken = session.query(OrganizationModel).filter(OrganizationModel.email == email).all()
            if email_taken:
                flash("Данный email уже занят")
            else:
                organization_account = OrganizationModel(title=title, email=email, password=generate_password_hash(password))
                # organization_account = OrganizationModel()
                # organization_account.save()
                session.add(organization_account)
                session.commit()
                user = User().create_with_organization_user(user=organization_account)
                login_user(user)
                return redirect(url_for("organization"))
        else:
            flash_message = str()
            if password_confirmation_validator(password, password_confirmation):
                flash_message = password_confirmation_validator(password, password_confirmation)
            if password_validator(password):
                flash_message = password_validator(password)
            if email_validator(email):
                flash_message = email_validator(email)
            if name_validator(title):
                flash_message = title_validator(email)
            flash(flash_message)

    data: [str, object] = {
        "title": "Регистрация - организация",
        "select_role_url": url_for("select_role"),
        "organization_login_url": url_for("organization_login"),
        "ui_kit_styles_url": url_for("static", filename="css/ui_kit_styles.css"),
        "organization_signup_styles_url": url_for("static", filename="css/organization_signup_styles.css"),
        "organization_signup_script_url": url_for("static", filename="js/organization_signup_script.js"),
        "form": form,
        "data_css": {
            "url_for": url_for
        }
    }
    return render_template("organization_signup.html", **data)


# Основная страница - организация
@logger.catch
@app.route("/organization", methods=["POST", "GET"])
@login_required
def organization():

    if current_user.is_client():
        abort(401)

    form = NewRecordForm()

    session = Session(bind=service_db)
    if form.validate_on_submit():
        id = form.id.data

        # client_exists = ClientModel.get_or_none(ClientModel.id == int(id))
        client_exists = session.query(ClientModel).filter(ClientModel.id == int(id)).first()

        if client_exists:
            # record_exists = RecordModel.get_or_none((RecordModel.client == id) &
            # (RecordModel.organization == current_user._user.id))
            record_exists = session.query(RecordModel).filter((RecordModel.client == id) &
                                                              (RecordModel.organization == current_user._user.id)).first()
            if record_exists:
                record_exists.accumulated += 1
                record_exists.last_record_date = date.today()

                if record_exists.accumulated >= current_user._user.limit:
                    record_exists.accumulated = 0
                    record_exists.save()
                    return redirect(url_for("accumulated"))

                record_exists.save()
                return redirect(url_for("added"))
            else:
                session.add(RecordModel(client=int(id), organization=int(current_user._user.id),
                                        last_record_date=date.today()))
                session.commit()
                return redirect(url_for("added"))
        else:
            return redirect(url_for("wrong_id"))


    data: [str, object] = {

        "title": "Организация",
        "ui_kit_styles_url": url_for("static", filename="css/ui_kit_styles.css"),
        "organization_styles_url": url_for("static", filename="css/organization_styles.css"),
        "organization_script_url": url_for("static", filename="js/organization_script.js"),
        "organization_title": current_user._user.to_dict()["title"],
        "organization_settings_url": url_for("organization_settings"),
        "form": form,
        # "clients": RecordModel.select().where(RecordModel.organization == int(current_user._user.id)).order_by(RecordModel.accumulated.desc()),
        "clients": session.query(RecordModel).filter(RecordModel.organization == int(current_user._user.id)).order_by(RecordModel.accumulated.desc()).all(),
        "str": str,
        "data_css": {
            "url_for": url_for,
        },
        "user_info": current_user._user.to_dict()
    }
    return render_template("organization.html", **data)


# Под-страница страницы организатора - неверный id
@logger.catch
@app.route("/organization/wrong_id")
@login_required
def wrong_id():
    data: [str, object] = {
        "title": "Ошибка",
        "ui_kit_styles_url": url_for("static", filename="css/ui_kit_styles.css"),
        "wrong_id_styles_url": url_for("static", filename="css/wrong_id_styles.css"),
        "wrong_id_script_url": url_for("static", filename="js/wrong_id_script.js"),
        "organization_main_url": url_for("organization")
    }
    return render_template("wrong_id.html", **data)


# Под-страница страницы организатора - купон добавлен
@logger.catch
@app.route("/organization/added")
@login_required
def added():
    data: [str, object] = {
        "title": "Добавлено",
        "ui_kit_styles_url": url_for("static", filename="css/ui_kit_styles.css"),
        "coupon_added_styles_url": url_for("static", filename="css/coupon_added_styles.css"),
        "coupon_added_script_url": url_for("static", filename="js/coupon_added_script.js"),
        "organization_main_url": url_for("organization")
    }
    return render_template("coupon_added.html", **data)


# Под-страница страницы организатора - накоплено
@logger.catch
@app.route("/organization/accumulated")
@login_required
def accumulated():
    data: [str, object] = {
        "title": "Накоплено",
        "ui_kit_styles_url": url_for("static", filename="css/ui_kit_styles.css"),
        "accumulated_styles_url": url_for("static", filename="css/accumulated_styles.css"),
        "accumulated_script_url": url_for("static", filename="js/accumulated_script.js"),
        "organization_main_url": url_for("organization")
    }
    return render_template("accumulated.html", **data)


# Основные настройки - организации
@logger.catch
@app.route("/organization/settings")
@login_required
def organization_settings() -> str:

    if current_user.is_client():
        abort(401)

    data: [str, object] = {
        "title": "Настройки",
        "ui_kit_styles_url": url_for("static", filename="css/ui_kit_styles.css"),
        "organization_settings_styles_url": url_for("static", filename="css/organization_settings_styles.css"),
        "organization_settings_script_url": url_for("static", filename="js/organization_settings_script.js"),
        "organization_main_url": url_for("organization"),
        "organization_logout_url": url_for("organization_logout"),
        "organization_settings_change_picture_url": url_for("organization_settings_change_picture"),
        "organization_settings_change_name_url": url_for("organization_settings_change_name"),
        "organization_settings_change_email_url": url_for("organization_settings_change_email"),
        "organization_settings_change_password_url": url_for("organization_settings_change_password"),
        "organization_settings_change_sticker_url": url_for("organization_settings_change_sticker"),
        "organization_settings_change_limit_url": url_for("organization_settings_change_limit"),
        "user_info": current_user._user.to_dict(),
        "data_css": {
            "url_for": url_for
        }
    }

    return render_template("organization_settings.html", **data)


# Основные настройки - организации, сменя картинки
@logger.catch
@app.route("/organization/settings/change_picture", methods=["POST", "GET"])
@login_required
def organization_settings_change_picture() -> str:

    if current_user.is_client():
        abort(401)

    data: [str, object] = {
        "title": "Сменить имя",
        "ui_kit_styles_url": url_for("static", filename="css/ui_kit_styles.css"),
        "organization_settings_change_picture_styles_url": url_for("static", filename="css/organization_settings_change_picture_styles.css"),
        "organization_settings_change_picture_script_url": url_for("static", filename="js/organization_settings_change_picture_script.js"),
        "organization_settings_change_picture_upload_url": url_for("organization_settings_change_picture_upload"),
        "organization_settings_url": url_for("organization_settings"),
        "user_info": current_user._user.to_dict()
    }

    return render_template("organization_settings_change_picture.html", **data)


# Основные настройки - организации, сменя картинки - загрузка
@logger.catch
@app.route("/organization/settings/change_picture/upload", methods=["POST", "GET"])
@login_required
def organization_settings_change_picture_upload():

    if current_user.is_client():
        abort(401)

    if request.method == "POST":
        file = request.files["file"]
        if file and image_validator(file.filename) is None:
            try:
                image = file.read()
                from sqlite3 import Binary # TODO: change (remove sqlite3)
                bin_image = Binary(image)

                session = Session(bind=service_db)
                # organization_account = OrganizationModel.get(OrganizationModel.id == current_user._user.id)
                organization_account = session.query(OrganizationModel).filter(OrganizationModel.id == current_user._user.id).first()
                organization_account.image = bin_image
                # organization_account.save()
                session.commit()
                current_user._user.image = bin_image

                return redirect(url_for("organization_settings"))
            except FileNotFoundError as error:
                flash("файл не найден")
                redirect(url_for("organization_settings_change_picture"))
        else:
            flash(image_validator(file.filename) if file else "неизвестная ошибка")
            redirect(url_for("organization_settings_change_picture"))

    return redirect(url_for("organization_settings"))


# Отображение картинок пользователей
@logger.catch
@app.route("/organization/picture/<int:id>")
# @login_required
def organization_picture_get(id: int):

    max_id = -1
    session = Session(bind=service_db)
    # for elem in OrganizationModel.select().order_by(OrganizationModel.id.desc()).limit(1):
    for elem in session.query(OrganizationModel).order_by(OrganizationModel.id.desc()).all().limit(1):
        if elem.id > max_id:
            max_id = elem.id

    if id > max_id:
        abort(404)

    # image = OrganizationModel.get(OrganizationModel.id == id).image
    image = session.query(OrganizationModel).filter(OrganizationModel.id == id).all().image
    h = make_response(image)
    h.headers["Content-Type"] = "image/png"

    return h


# Основные настройки - организация, сменя имени
@logger.catch
@app.route("/organization/settings/change_name", methods=["POST", "GET"])
@login_required
def organization_settings_change_name():

    if current_user.is_client():
        abort(401)

    form = OrganizationChangeName()

    if form.validate_on_submit():
        title = form.title.data

        if title_validator(title) is None:
            session = Session(bind=service_db)
            # organization_account = OrganizationModel.get(OrganizationModel.id == current_user._user.id)
            organization_account = session.query(OrganizationModel).filter(OrganizationModel.id == current_user._user.id).first()
            organization_account.title = title
            # organization_account.save()
            session.commit()
            current_user._user.title = title
            return redirect(url_for("organization_settings"))
        else:
            flash_message = str()
            if title_validator(title):
                flash_message = title_validator(title)
            flash(flash_message)

    data: [str, object] = {
        "title": "Сменить имя",
        "ui_kit_styles_url": url_for("static", filename="css/ui_kit_styles.css"),
        "organization_settings_change_name_styles_url": url_for("static", filename="css/organization_settings_change_name_styles.css"),
        "organization_settings_change_name_script_url": url_for("static", filename="js/organization_settings_change_name_script.js"),
        "form": form,
        "organization_settings_url": url_for("organization_settings"),
        "data_js": {
            "user_info": current_user._user.to_dict()
        },
        "data_css": {
            "url_for": url_for
        }
    }

    return render_template("organization_settings_change_name.html", **data)


# Основные настройки - организация, изменение лимита
@logger.catch
@app.route("/organization/settings/change_limit", methods=["POST", "GET"])
@login_required
def organization_settings_change_limit():

    if current_user.is_client():
        abort(401)

    form = OrganizationChangeLimit()

    if form.validate_on_submit():
        limit = form.limit.data

        if limit_validator(limit) is None:
            session = Session(bind=service_db)
            # organization_account = OrganizationModel.get(OrganizationModel.id == current_user._user.id)
            organization_account = session.query(OrganizationModel).filter(OrganizationModel.id == current_user._user.id).first()
            organization_account.limit = limit
            # organization_account.save()
            session.commit()
            current_user._user.limit = limit
            return redirect(url_for("organization_settings"))
        else:
            flash_message = str()
            if limit_validator(limit):
                flash_message = limit_validator(limit)
            flash(flash_message)

    data: [str, object] = {
        "title": "Изменить лимит",
        "ui_kit_styles_url": url_for("static", filename="css/ui_kit_styles.css"),
        "organization_settings_change_limit_styles_url": url_for("static", filename="css/organization_settings_change_limit_styles.css"),
        "organization_settings_change_limit_script_url": url_for("static", filename="js/organization_settings_change_limit_script.js"),
        "form": form,
        "organization_settings_url": url_for("organization_settings"),
        "data_js": {
            "user_info": current_user._user.to_dict()
        },
        "data_css": {
            "url_for": url_for
        }
    }

    return render_template("organization_settings_change_limit.html", **data)

# Основные настройки - организация, сменя почты
@logger.catch
@app.route("/organization/settings/change_email", methods=["POST", "GET"])
@login_required
def organization_settings_change_email():

    if current_user.is_client():
        abort(401)

    form = OrganizationChangeEmail()

    if form.validate_on_submit():
        email = form.email.data

        if email_validator(email) is None:
            session = Session(bind=service_db)
            # organization_account = OrganizationModel.get(OrganizationModel.id == current_user._user.id)
            organization_account = session.query(OrganizationModel).filter(OrganizationModel.id == current_user._user.id).first()
            organization_account.email = email
            # organization_account.save()
            session.commit()
            current_user._user.email = email
            return redirect(url_for("organization_settings"))
        else:
            flash_message = str()
            if email_validator(email):
                flash_message = email_validator(email)
            flash(flash_message)

    data: [str, object] = {
        "title": "Сменить email",
        "ui_kit_styles_url": url_for("static", filename="css/ui_kit_styles.css"),
        "organization_settings_change_email_styles_url": url_for("static", filename="css/organization_settings_change_email_styles.css"),
        "organization_settings_change_email_script_url": url_for("static", filename="js/organization_settings_change_email_script.js"),
        "form": form,
        "organization_settings_url": url_for("organization_settings"),
        "data_js": {
            "user_info": current_user._user.to_dict()
        },
        "data_css": {
            "url_for": url_for
        }
    }

    return render_template("organization_settings_change_email.html", **data)


# Основные настройки - клиент, сменя пароля
@logger.catch
@app.route("/organization/settings/change_password", methods=["POST", "GET"])
@login_required
def organization_settings_change_password():

    if current_user.is_client():
        abort(401)

    form = OrganizationChangePassword()

    if form.validate_on_submit():
        password = form.password.data

        if password_validator(password) is None:
            session = Session(bind=service_db)
            # organization_account = OrganizationModel.get(OrganizationModel.id == current_user._user.id)
            organization_account = session.query(OrganizationModel).filter(OrganizationModel.id == current_user._user.id).first()
            organization_account.password = generate_password_hash(password)
            # organization_account.save()
            session.commit()
            current_user._user.password = generate_password_hash(password)
            return redirect(url_for("organization_settings"))
        else:
            flash_message = str()
            if password_validator(password):
                flash_message = password_validator(password)
            flash(flash_message)

    data: [str, object] = {
        "title": "Сменить пароль",
        "ui_kit_styles_url": url_for("static", filename="css/ui_kit_styles.css"),
        "organization_settings_change_password_styles_url": url_for("static", filename="css/organization_settings_change_password_styles.css"),
        "organization_settings_change_password_script_url": url_for("static", filename="js/organization_settings_change_password_script.js"),
        "form": form,
        "organization_settings_url": url_for("organization_settings"),
        "data_css": {
            "url_for": url_for
        }
    }

    return render_template("organization_settings_change_password.html", **data)


# Основные настройки - организация, сменя почты
@logger.catch
@app.route("/organization/settings/change_sticker", methods=["POST", "GET"])
@login_required
def organization_settings_change_sticker():

    if current_user.is_client():
        abort(401)

    form = OrganizationChangeSticker()

    if form.validate_on_submit():
        sticker = form.sticker.data

        if sticker_validator(sticker) is None:
            session = Session(bind=service_db)
            # organization_account = OrganizationModel.get(OrganizationModel.id == current_user._user.id)
            organization_account = session.query(OrganizationModel).filter(OrganizationModel.id == current_user._user.id).first()
            organization_account.sticker = sticker
            # organization_account.save()
            session.commit()
            current_user._user.sticker = sticker
            return redirect(url_for("organization_settings"))
        else:
            flash_message = str()
            if sticker_validator(sticker):
                flash_message = sticker_validator(sticker)
            flash(flash_message)

    data: [str, object] = {
        "title": "Сменить стикер",
        "ui_kit_styles_url": url_for("static", filename="css/ui_kit_styles.css"),
        "organization_settings_change_sticker_styles_url": url_for("static", filename="css/organization_settings_change_sticker_styles.css"),
        "organization_settings_change_sticker_script_url": url_for("static", filename="js/organization_settings_change_sticker_script.js"),
        "form": form,
        "organization_settings_url": url_for("organization_settings"),
        "data_js": {
            "user_info": current_user._user.to_dict()
        },
        "data_css": {
            "url_for": url_for
        }
    }

    return render_template("organization_settings_change_sticker.html", **data)


# Отслеживание ошибок
@logger.catch
@app.errorhandler(404)
def page_not_found_error(error_message):
    logger.info(error_message)
    return "404 Error", 404


@logger.catch
@app.errorhandler(401)
def page_not_found_error(error_message):
    logger.info(error_message)
    return "401 Error", 401
