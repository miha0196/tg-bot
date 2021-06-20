import logging
from telegram.ext import CommandHandler, Updater, CallbackContext, CallbackQueryHandler, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from datetime import datetime
import requests
from keys import OPEN_WEATHER_API_KEY, TG_BOT_API_KEY

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

updater = Updater(token=TG_BOT_API_KEY, use_context=True)
dispatcher = updater.dispatcher
dic = {'city': ''}

def get_weather(city):
  r = requests.get(f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPEN_WEATHER_API_KEY}&lang=ru&units=metric')
  return r.json()

def form_date(seconds):
  return datetime.strftime(datetime.fromtimestamp(seconds), "%d-%m-%Y")

def deg_to_cardinal_direction(deg):
  cardinal_directions = {
    0: 'С',
    45: 'СЗ',
    90: 'З',
    135: 'ЮЗ',
    180: 'Ю',
    225: 'ЮВ',
    270: 'В',
    315: 'СВ',
    360: 'С'
  }

  for key in cardinal_directions.keys():
    if (key > deg - 22.5):
      return cardinal_directions[key]

def start(update: Update, _: CallbackContext) -> None:
  dispatcher.add_handler(messageHandler)
  update.message.reply_text('Пожалуйста, введите английскими буквами населенный пункт, в котором хотите узнать погоду на ближайшие дни:\n')

def selectCityHandler(update: Update, _: CallbackContext) -> None:
  if int(get_weather(update.message.text)['cod']) == 404:
    return update.message.reply_text('Указанного города не существует, введите город снова:')  

  dispatcher.remove_handler(messageHandler)
  dic['city'] = update.message.text

  keyboard = [
    [
      InlineKeyboardButton("1", callback_data=1),
      InlineKeyboardButton("2", callback_data=2),
      InlineKeyboardButton("3", callback_data=3),
      InlineKeyboardButton("4", callback_data=4),
      InlineKeyboardButton("5", callback_data=5)
    ],
    [InlineKeyboardButton("Выбрать другой регион", callback_data='return')]
  ]

  reply_markup = InlineKeyboardMarkup(keyboard)

  update.message.reply_text(text='Выберите количество дней, на которое хотите узнать погоду:', reply_markup=reply_markup)

messageHandler = MessageHandler(Filters.text & ~Filters.command, selectCityHandler)

def button(update: Update, _: CallbackContext) -> None:
  query = update.callback_query

  query.answer()

  keyboard = [
    [
      InlineKeyboardButton("1", callback_data=1),
      InlineKeyboardButton("2", callback_data=2),
      InlineKeyboardButton("3", callback_data=3),
      InlineKeyboardButton("4", callback_data=4),
      InlineKeyboardButton("5", callback_data=5)
    ],
    [InlineKeyboardButton("Выбрать другой регион", callback_data='return')]
  ]

  reply_markup=InlineKeyboardMarkup(keyboard)

  if (query.data == 'return'):
    dispatcher.add_handler(messageHandler)
    query.edit_message_text(text='Пожалуйста, введите английскими буквами населенный пункт, в котором хотите узнать погоду на ближайшие дни:\n')
    return

  if (not query.data.isdigit() and query.data != 'return'):
    dic['city'] = query.data

  if query.data.isdigit():
    r = get_weather(dic['city'])
    answer = 'Погода {}:\n\n'.format(r['city']['name'])

    for index, day in enumerate(r['list'][:int(query.data) * 8]):
      if index % 8 != 0: 
        continue
      answer += '{}, {}\N{DEGREE SIGN}C, {}, ветер {}, {}м/с\n\n'.format(form_date(day['dt']), round(day['main']['temp']), day['weather'][0]['description'], deg_to_cardinal_direction(day['wind']['deg']), round(day['wind']['speed']))

    query.edit_message_text(text=answer)
    query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Хочу снова узнать погоду", callback_data=dic['city'])]]))
    return

  query.edit_message_text(text='На сколько дней вы хотите получить прогноз:')
  query.edit_message_reply_markup(reply_markup=reply_markup)

def main() -> None:
  dispatcher.add_handler(CommandHandler('start', start))
  dispatcher.add_handler(CallbackQueryHandler(button))

  updater.start_polling()
  updater.idle()

if __name__ == '__main__':
  main()