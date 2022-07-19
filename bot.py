import os

from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

import myconstants

load_dotenv()
secret_token = os.getenv('TOKEN')


def send_answer(update, context):
    chat = update.effective_chat

    if update.message.text == 'Расскажите про курсы и тарифы':
        context.bot.send_message(chat.id, myconstants.KURS_INFO)
        context.bot.send_message(chat.id, myconstants.KURS_PREVIEW)

    elif update.message.text == 'Расскажите про марафоны':
        context.bot.send_message(chat.id, myconstants.MARA)
        context.bot.send_message(chat.id, myconstants.MARA_PREVIEW)

    elif update.message.text == 'Сколько стоят курсы?':
        context.bot.send_message(chat.id, myconstants.PRICE)
        context.bot.send_message(chat.id, myconstants.RASS)

    elif update.message.text == 'Могу я оплатить в евро?':
        context.bot.send_message(chat.id, myconstants.EURO)

    elif update.message.text == 'Курс останется у меня навсегда?':
        context.bot.send_message(chat.id, myconstants.KURS_TIME)

    elif update.message.text == 'Я смогу сдать экзамен после курса?':
        context.bot.send_message(chat.id, myconstants.EXAM)

    elif update.message.text == 'Курс подойдет ребенку?':
        context.bot.send_message(chat.id, myconstants.CHILD)

    elif update.message.text == 'Как проверяются домашние задания?':
        context.bot.send_message(chat.id, myconstants.HOMEWORK)

    elif update.message.text == 'Как определить свой уровень?':
        context.bot.send_message(chat.id, myconstants.MY_LEVEL)

    elif update.message.text == 'У меня другой вопрос.':
        context.bot.send_message(chat.id, myconstants.ELSE_QUESTION)


def wake_up(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    buttons = ReplyKeyboardMarkup(
        [['Расскажите про курсы и тарифы', 'Расскажите про марафоны'],
         ['Сколько стоят курсы?', 'Могу я оплатить в евро?'],
         ['Курс останется у меня навсегда?',
          'Я смогу сдать экзамен после курса?'],
         ['Курс подойдет ребенку?',
          'Как проверяются домашние задания?'],
         ['Как определить свой уровень?', 'У меня другой вопрос.']],
        resize_keyboard=True
    )
    context.bot.send_message(
        chat_id=chat.id,
        text='Привет, {}. Какой у вас вопрос?'.format(name),
        reply_markup=buttons
    )


def main():
    updater = Updater(token=secret_token)

    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(
        MessageHandler(Filters.text('Расскажите про курсы и тарифы'),
                       send_answer)
    )
    updater.dispatcher.add_handler(
        MessageHandler(Filters.text('Расскажите про марафоны'), send_answer)
    )
    updater.dispatcher.add_handler(
        MessageHandler(Filters.text('Сколько стоят курсы?'), send_answer)
    )
    updater.dispatcher.add_handler(
        MessageHandler(Filters.text('Могу я оплатить в евро?'), send_answer)
    )
    updater.dispatcher.add_handler(
        MessageHandler(Filters.text('Курс останется у меня навсегда?'),
                       send_answer)
    )
    updater.dispatcher.add_handler(
        MessageHandler(Filters.text('Я смогу сдать экзамен после курса?'),
                       send_answer)
    )
    updater.dispatcher.add_handler(
        MessageHandler(Filters.text('Курс подойдет ребенку?'),
                       send_answer)
    )
    updater.dispatcher.add_handler(
        MessageHandler(Filters.text('Как проверяются домашние задания?'),
                       send_answer)
    )
    updater.dispatcher.add_handler(
        MessageHandler(Filters.text('Как определить свой уровень?'),
                       send_answer)
    )
    updater.dispatcher.add_handler(
        MessageHandler(Filters.text('У меня другой вопрос.'), send_answer)
    )

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
