def name_validator(name: str): #-> None | str:
    if name == "aa":
        return "Введите настоящие имя"
    return None


def title_validator(title: str): #-> None | str:
    if title == "aa":
        return "Введите настоящие название"
    return None


def email_validator(email: str): #-> None | str:
    if "@" not in email:
        return "Некорректный адрес почты"
    return None


def password_validator(password: str): #-> None | str:
    if len(password) < 8:
        return "Пароль слишком короткий"
    return None


def password_confirmation_validator(password: str, first_password: str): #-> None | str:
    if password != first_password:
        return "Пароли не совпадают"
    return None


def sticker_validator(sticker: str): #-> None | str:
    if len(sticker) > 1:
        return "Длина поля стикера должна быть равна 1-му"
    return None


def image_validator(path: str): #-> None | str:
    return None


def limit_validator(limit: int): #-> None | str:
    return None


# TODO: написать нормальные валидаторы
