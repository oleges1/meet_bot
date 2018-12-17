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
import dateutil

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def add_meeting(bot, update):
    user = update.message.from_user
    add_user_message(update)
    logger.info("meeting of %s: %s", user.first_name, update.message.text)

    update.message.reply_text('First of all, tell me name of your meeting')

    return MEETING


def add_name_to_meeting(bot, update):
    user = update.message.from_user
    add_user_message(update)
    logger.info("add name to meeting: from %s, added %s",
                user.first_name, update.message.text)
    update.message.reply_text('Okey, tell me @names of people')

    return MEETING_NAME


def add_user_to_meeting(bot, update):
    from_user = update.message.from_user
    last_mess = last_message(from_user)
    users = update.message.text.strip().split()
    if last_mess.text.startswith('users'):
        update_user_message_text(update, last_mess + update.message.text)
    else:
        add_user_message_text(update, 'users ' + update.message.text)
    for username in users:
        logger.info(f"add user to meeting: from {from_user.username}, added {username}")
        timeslots = get_users_timeslots(username)
        if timeslots is not None:
            update.message.reply_text(f'today user {username} is busy in:' + timeslots)
    update.message.reply_text('Press /done if you are, else type another @name')
    return MEETING_USERS


def add_workspace_to_meeting(bot, update):
    from_user = update.message.from_user
    logger.info("updated users list for %s", user.first_name)
    last_mess = last_message(from_user)
    update_user_message_text(update, last_mess[6:])
    update.message.reply_text('Great! Now I need to know workspace!')
    return MEETING_WORKSPACE


def add_location_to_meeting(bot, update):
    user = update.message.from_user
    logger.info("updated users list for %s", user.first_name)
    add_user_message(update)
    update.message.reply_text('Great! Now I need to know location!')
    return MEETING_LOCATION


def add_start_to_meeting(bot, update):
    user = update.message.from_user
    logger.info("updated location for %s: %s", user.first_name, update.message.text)
    workspace = last_message(user.id).text
    add_user_message(update)
    timeslots = get_location_timeslots(update.message.text.lower().strip(), workspace)
    if timeslots is not None:
        update.message.reply_text(
            f'Today location {update.message.text} is busy in:' + timeslots)
        update.message.reply_text('Great! Now I need to know start time!')
        return MEETING_START
    else:
        update.message.reply_text('No such location in this workspace')
        reply_keyboard = [['My meetings', 'Add meeting'],
                          ['Add workspace', 'Add location']]
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
    logger.info("updated end_time for %s: %s", user.first_name, update.message.text)
    add_user_message(update)
    name, users, workspace, location, start_time, end_time = last_messages(
        from_user, count=6)
    start_time = dateutil.parser.parse(start_time)
    end_time = dateutil.parser.parse(end_time)
    meeting, user_ids = add_meeting(
        name, users, workspace, location, start_time, end_time)
    for user_id in user_ids:
        bot.send_message(
            chat_id=user_id, text="You are invited into new meeting with id %s, check it using \"My meetings\" button" % meeting.id)
    update.message.reply_text(
        'Great! New meeting with id %s is added to your schedule.' % meeting.id)
    reply_keyboard = [['My meetings', 'Add meeting'],
                      ['Add workspace', 'Add location']]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)
    return ACTION


meeting_states = {
    MEETING: [MessageHandler(Filters.text, add_user_to_meeting)],
    MEETING_NAME: [MessageHandler(Filters.text, add_name_to_meeting)],
    MEETING_USERS: [CommandHandler('done', add_workspace_to_meeting),
                    MessageHandler(Filters.text, add_user_to_meeting)],
    MEETING_WORKSPACE: [MessageHandler(Filters.text, add_location_to_meeting)],
    MEETING_LOCATION: [MessageHandler(Filters.text, add_start_to_meeting)],
    MEETING_START: [MessageHandler(Filters.text, add_end_to_meeting)],
    MEETING_END: [MessageHandler(Filters.text, end_adding_meeting)]
}
