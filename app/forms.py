from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField


# Формы входа/регистрации
class ClientLoginForm(FlaskForm):
    email = StringField("email")
    password = PasswordField("password")
    submit = SubmitField("login")


class ClientSignupForm(FlaskForm):
    name = StringField("name")
    email = StringField("email")
    password = PasswordField("password")
    password_confirmation = PasswordField("password_confirmation")
    submit = SubmitField("signup")


class OrganizationLoginForm(FlaskForm):
    email = StringField("email")
    password = PasswordField("password")
    submit = SubmitField("login")


class OrganizationSignupForm(FlaskForm):
    title = StringField("name")
    email = StringField("email")
    password = PasswordField("password")
    password_confirmation = PasswordField("password_confirmation")
    submit = SubmitField("signup")


# Форма нового купона
class NewRecordForm(FlaskForm):
    id = IntegerField("id")
    submit = SubmitField("checkout")


# Формы обновления данных профиля - клиент
class ClientChangeName(FlaskForm):
    name = StringField("name")
    submit = SubmitField("save")


# Формы обновления данных профиля - клиент
class ClientChangeEmail(FlaskForm):
    email = StringField("email")
    submit = SubmitField("save")


# Формы обновления данных профиля - клиент
class ClientChangePassword(FlaskForm):
    password = StringField("password")
    submit = SubmitField("save")


# Формы обновления данных профиля - организация
class OrganizationChangeName(FlaskForm):
    title = StringField("title")
    submit = SubmitField("save")


# Формы обновления данных профиля - организация
class OrganizationChangeEmail(FlaskForm):
    email = StringField("email")
    submit = SubmitField("save")


# Формы обновления данных профиля - организация
class OrganizationChangePassword(FlaskForm):
    password = StringField("password")
    submit = SubmitField("save")


# Формы обновления данных профиля - организация
class OrganizationChangeSticker(FlaskForm):
    sticker = StringField("sticker")
    submit = SubmitField("save")



# Формы обновления данных профиля - организация
class OrganizationChangeLimit(FlaskForm):
    limit = StringField("limit")
    submit = SubmitField("save")
