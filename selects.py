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
def get_user(telegram_id):
    return User.get(telegram_id=telegram_id)


@db_session
def get_or_create_user(telegram_id):
    temp_workspace = get_user(telegram_id)
    return temp_workspace if temp_workspace is not None else User(telegram_id=telegram_id)


@db_session
def create_message(user, text):
    if not isinstance(user, User):
        user = get_user(user)
    return Message(
        user=user,
        text=update.message.text.lower().strip()
    )


@db_session
def get_workspace(name):
    return Workspace.get(name=name)


@db_session
def get_or_create_workspace(name):
    temp_workspace = get_workspace(name)
    return temp_workspace if temp_workspace is not None else Workspace(name=name)


@db_session
def get_location(name, workspace):
    return Location.get(name=name, workspace=workspace)


@db_session
def create_location(name, workspace):
    print(workspace, name)
    return Location(
        workspace=workspace,
        name=name
    )


@db_session
def last_message(user):
    if not isinstance(user, User):
        user = get_user(user)
    if user is None:
        raise ValueError('no such user')
    return Message.last_message(user)


@db_session
def add_location_to_workspace(location, workspace_id):
    workspace = Workspace.get(id=workspace_id)
    location = create_location(location, workspace)
    workspace.locations.add(location)


@db_session
def add_user_to_workspace(user, workspace):
    if not isinstance(user, User):
        user = get_or_create_user(user)
    if not isinstance(workspace, Workspace):
        workspace = get_or_create_workspace(workspace)
    workspace.users.add(user)


@db_session
def add_workspace_to_user(user, workspace):
    if not isinstance(user, User):
        user = get_or_create_user(user)
    if not isinstance(workspace, Workspace):
        workspace = get_or_create_workspace(workspace)
    user.workspaces.add(workspace)
