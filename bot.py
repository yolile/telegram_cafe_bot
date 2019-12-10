# -*- coding: utf-8 -*-

import logging
import os

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters

import models

token = os.environ['TELEGRAM_CAFE_TOKEN']
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
models.load_compra_table()
orden = ["nombre1", "nombre2", "nombre3"]
usuario = None


def list(bot, update):
    command = update.message.text.replace('/', '')
    if command == 'aquienletoca':
        ultimo = models.Compra.select().order_by(models.Compra.date.desc()).get().name
        ultimo_posicion = orden.index(ultimo)
        siguiente_posicion = ultimo_posicion + 1 if ultimo_posicion < len(orden) else 0
        update.message.reply_text('Le toca a: {}'.format(orden[siguiente_posicion]))
    if command == 'listarcompras':
        mensaje = ''
        for compra in models.Compra.select().order_by(models.Compra.date.desc()).paginate(1, 3):
            mensaje += '\n {} - {} '.format(compra.date, compra.name)
        update.message.reply_text(mensaje)


def agregar(bot, update):
    reply_keyboard = [orden]

    update.message.reply_text(
        'Quién compró el café?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return 1


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def nombre_handler(bot, update):
    nombre = update.message.text
    global usuario
    usuario = nombre
    update.message.reply_text('Cuándo compró {} el café?'.format(nombre),
                              reply_markup=ReplyKeyboardRemove())
    return 2


def fecha_handler(bot, update):
    global usuario
    fecha = update.message.text
    models.Compra.create(name=usuario, date=fecha)
    update.message.reply_text('Se ha agregado que {} compró café el {}. Gracias {}!'.format(usuario, fecha, usuario))
    return ConversationHandler.END


def cancelar(bot, update):
    update.message.reply_text('Se canceló la actualización de la compra',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def main():
    models.load_compra_table()
    # Create the Updater and pass it your bot's token.
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("aquienletoca", list))
    dp.add_handler(CommandHandler("listarcompras", list))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('agregarcompra', agregar)],

        states={
            1: [MessageHandler(Filters.regex('^(nombre1|nombre2|nombre3)$'), nombre_handler)],

            2: [MessageHandler(Filters.text, fecha_handler)]
        },

        fallbacks=[CommandHandler('cancel', cancelar)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
