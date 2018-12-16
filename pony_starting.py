from datetime import datetime, timedelta
from pony.orm import *


db = Database()


class User(db.Entity):
    id = PrimaryKey(int, auto=True)
    telegram_id = Optional(int)
    first_name = Optional(str)
    last_name = Optional(str, nullable=True)
    username = Optional(str, nullable=True)
    messages = Set('Message')
    meetings = Set('Meeting')
    workspaces = Set('Workspace')

    @staticmethod
    def user_from_update(update):
        from_user = update.message.from_user
        return User(
            telegram_id=from_user.id,
            first_name=from_user.first_name,
            last_name=from_user.last_name,
            username=from_user.username
        )


class Message(db.Entity):
    id = PrimaryKey(int, auto=True)
    text = Optional(str, nullable=True)
    user = Required(User)
    time = Optional(datetime, default=lambda: datetime.now())

    @staticmethod
    def message_from_update(update, user):
        return Message(
            user=user,
            text=update.message.text.lower().strip()
        )

    @staticmethod
    def last_message(user):
        if not isinstance(user, User):
            raise ValueError('User should be instance of class User')
        return list(Message.select(lambda message:
                                   message.user == user).order_by(lambda message: desc(message.id)))[0]


class Workspace(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    users = Set(User)
    locations = Set('Location')


class Location(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    meetings = Set('Meeting')
    workspace = Required(Workspace)


class Meeting(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    users = Set(User)
    location = Required(Location)
    start_time = Optional(datetime)
    end_time = Optional(datetime)


db.bind(provider='sqlite', filename='sql', create_db=True)
db.generate_mapping(create_tables=True)
