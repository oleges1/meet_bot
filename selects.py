from pony.orm import *
from pony_starting import *


@db_session
def add_user(telegram_id, name):
    User(telegram_id=telegram_id, name=name)


@db_session
def get_user(telegram_id):
    return User.get(telegram_id=telegram_id)
