#! /usr/bin/python3
import logging
import os

from urllib3 import make_headers
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, InputTextMessageContent,
                      ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, CallbackQueryHandler,
                          Filters, RegexHandler, ConversationHandler)

from selects import *
from bot.states import *
from dateutil import parser as dt_parser
import traceback

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def convert_timeslots(timeslots):
    res = ''
    for timeslot_pair in timeslots:
        start, end = timeslot_pair
        res += 'from: ' + start.strftime("%H:%M") + \
            ' to: ' + end.strftime("%H:%M") + '\n'
    return res


def add_meeting(bot, update):
    user = update.message.from_user
    add_user_message(update)
    logger.info("user %s. creating meeting: STARTED", user.first_name)

    update.message.reply_text('First of all, tell me name of your meeting')

    return MEETING


def add_name_to_meeting(bot, update):
    user = update.message.from_user
    add_user_message(update)
    logger.info("user %s. creating meeting %s",
                user.first_name, update.message.text)
    update.message.reply_text('Okey, tell me @names of people')

    return MEETING_NAME


def add_user_to_meeting(bot, update):
    from_user = update.message.from_user
    last_mess = last_message(from_user.id)
    users = update.message.text.strip().split()
    if last_mess.text.startswith('users'):
        update_user_message_text(update, last_mess.text +
                                 update.message.text.lower().strip())
    else:
        add_user_message_text(update, 'users ' + update.message.text.lower().strip())
    for username in users:
        logger.info(f"add user to meeting: from {from_user.username}, added {username}")
        username = username[1:] if username.startswith('@') else username
        timeslots = get_users_timeslots(username)
        if timeslots is not None:
            if len(timeslots) > 0:
                update.message.reply_text(
                    f'Today user {username} is busy in:\n' + convert_timeslots(timeslots))
            else:
                update.message.reply_text(
                    f'Today user {username} is free')
        else:
            update.message.reply_text(
                f'No such user {username} in my base, so you can hold meetings with him, but he will not get any information about it')
    update.message.reply_text('Press /done if you are, else type another @name')
    return MEETING_USERS


def add_workspace_to_meeting(bot, update):
    from_user = update.message.from_user
    logger.info("updated users list for %s", from_user.first_name)
    last_mess = last_message(from_user.id).text
    users = last_mess[6:].split()
    users = [user[1:] if user.startswith('@') else user for user in users]
    users.append(from_user.username)
    update_user_message_text(update, ' '.join(list(set(users))))
    update.message.reply_text('Great! Now I need to know workspace!')
    items = ''
    for i, wspace in enumerate(most_popular_workspaces()):
        items += f'{i}. {wspace.name} \n '
    update.message.reply_text(f'Most popular now are: \n {items}')
    return MEETING_WORKSPACE


def add_location_to_meeting(bot, update):
    user = update.message.from_user
    logger.info("updated workspace for %s: %s", user.first_name, update.message.text)
    add_user_message(update)
    wspace = last_message(user.id).text
    update.message.reply_text('Great! Now I need to know location!')
    items = ''
    for i, loc in enumerate(most_popular_locations(wspace)):
        items += f'{i}. {loc.name} \n '
    update.message.reply_text(f'Most popular now are: \n {items}')
    return MEETING_LOCATION


def add_start_to_meeting(bot, update):
    user = update.message.from_user
    logger.info("updated location for %s: %s", user.first_name, update.message.text)
    workspace = last_message(user.id).text
    add_user_message(update)
    timeslots = get_location_timeslots(update.message.text.lower().strip(), workspace)
    if timeslots is not None:
        if len(timeslots) > 0:
            update.message.reply_text(
                f'Today location {update.message.text} is busy in:\n' + convert_timeslots(timeslots))
        else:
            update.message.reply_text(
                f'Today location {update.message.text} is free')
        update.message.reply_text('Great! Now I need to know start time!')
        return MEETING_START
    else:
        update.message.reply_text('No such location in this workspace')
        reply_keyboard = [['My meetings', 'Add meeting'],
                          ['Add workspace', 'Add location'],
                          ['Cancel meeting']]
        reply_markup = ReplyKeyboardMarkup(reply_keyboard)
        update.message.reply_text('Please choose:', reply_markup=reply_markup)
        return ACTION


def add_end_to_meeting(bot, update):
    user = update.message.from_user
    logger.info("updated start_time for %s: %s", user.first_name, update.message.text)
    add_user_message(update)
    update.message.reply_text('Great! Now I need to know end time!')
    return MEETING_END


def end_adding_meeting(bot, update):
    from_user = update.message.from_user
    logger.info("updated end_time for %s: %s", from_user.first_name, update.message.text)
    add_user_message(update)
    name, users, workspace, location, start_time, end_time = last_messages(
        from_user.id, count=6)[::-1]
    try:
        start_time = dt_parser.parse(start_time.text)
        end_time = dt_parser.parse(end_time.text)
    except ValueError:
        del_message(start_time.id)
        del_message(end_time.id)
        traceback.print_exc()
        update.message.reply_text(
            'I could not parse your start or end time! Now I need to know start time!')
        return MEETING_START
    users = users.text.split()
    # print(name.text, users, workspace.text, location.text, start_time, end_time)
    meeting, user_ids = add_meeting_to_base(
        name.text, users, workspace.text, location.text, start_time, end_time)
    if meeting is not None:
        for user_id in user_ids:
            if user_id != from_user.id:
                bot.send_message(
                    chat_id=user_id, text="You are invited into new meeting with id %s, check it using \"My meetings\" button" % meeting.id)
        update.message.reply_text(
            'Great! New meeting with id %s is added to your schedule.' % meeting.id)
    else:
        update.message.reply_text('New meeting creation failed due to someone is busy')
    reply_keyboard = [['My meetings', 'Add meeting'],
                      ['Add workspace', 'Add location'],
                      ['Cancel meeting']]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)
    return ACTION


meeting_states = {
    MEETING: [MessageHandler(Filters.text, add_name_to_meeting)],
    MEETING_NAME: [MessageHandler(Filters.text, add_user_to_meeting)],
    MEETING_USERS: [CommandHandler('done', add_workspace_to_meeting),
                    MessageHandler(Filters.text, add_user_to_meeting)],
    MEETING_WORKSPACE: [MessageHandler(Filters.text, add_location_to_meeting)],
    MEETING_LOCATION: [MessageHandler(Filters.text, add_start_to_meeting)],
    MEETING_START: [MessageHandler(Filters.text, add_end_to_meeting)],
    MEETING_END: [MessageHandler(Filters.text, end_adding_meeting)]
}
