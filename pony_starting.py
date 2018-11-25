from datetime import datetime
from pony.orm import *


db = Database()


class User(db.Entity):
    id = PrimaryKey(int, auto=True)
    telegram_id = Optional(int)
    name = Optional(str)
    surname = Optional(str)
    messages = Set('Message')
    meetings = Set('Meeting')
    workspaces = Set('Workspace')


class Message(db.Entity):
    id = PrimaryKey(int, auto=True)
    text = Optional(str)
    user = Required(User)
    time = Optional(datetime)


class Workspace(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    users = Set(User)
    places = Set('Place')


class Place(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    meetings = Set('Meeting')
    workspace = Required(Workspace)


class Meeting(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    users = Set(User)
    place = Required(Place)
    start_time = Optional(datetime)
    end_time = Optional(datetime)


db.bind(provider='sqlite', filename='sql', create_db=True)
db.generate_mapping(create_tables=True)
