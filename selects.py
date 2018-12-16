from pony.orm import *
from pony_starting import *


@db_session
def add_user_message(update):
    user = User.get(telegram_id=update.message.from_user.id)
    if user is None:
        user = User.user_from_update(update)
        #user = User.get(telegram_id=update.message.from_user.id)
    print("user created", user.id)
    message = Message.message_from_update(update, user)
    return user, message


@db_session
def create_message(user, text):
    if isinstance(user, str):
        user = get_user(user)
    return Message(
        user=user,
        text=update.message.text
    )


@db_session
def get_user(telegram_id):
    return User.get(telegram_id=telegram_id)


@db_session
def get_workspace(name):
    return Workspace.get(name=name)


@db_session
def get_location(name):
    return Location.get(name=name)


@db_session
def last_message(user):
    if isinstance(user, str):
        user = get_user(user)
    return Message.last_message(user)


@db_session
def add_location_to_wokspace(location, workspace):
    if isinstance(location, str):
        location = get_location(location)
    workspace.locations.add(location)


@db_session
def add_user_to_workspace(user, workspace):
    if isinstance(user, str):
        user = get_user(user)
    if isinstance(workspace, str):
        workspace = get_workspace(workspace)
    workspace.users.add(user)


@db_session
def add_workspace_to_user(user, workspace):
    if isinstance(user, str):
        user = get_user(user)
    if isinstance(workspace, str):
        workspace = get_workspace(workspace)
    user.workspaces.add(workspace)
