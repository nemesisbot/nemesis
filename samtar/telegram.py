import requests
import time
from pprint import pprint
import json

URL = lambda token : "https://api.telegram.org/bot{}".format(token)

def get(url, parameters={}):

    res = requests.get(url, params=parameters)
    if res.status_code == 429:
        while res.status_code != 200:
            print("got 429")
            time.sleep(2)
            res = requests.get(url, params=parameters)

    return res.json()

def get_updates(token, offset=None):
    url= URL(token) + "/getUpdates"
    parameters = {
            'timeout': 100
            }
    if offset:
        parameters['offset'] = offset
    return get(url, parameters)

def updates(token):
    offset = None
    while True:
        try:
            updates = get_updates(token, offset)
            results = updates['result']
            offset = offset if not results else max(list(map(lambda x: int(x['update_id']), results))) + 1
            for result in results:
                yield token, result
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(e)
            time.sleep(1)

def send_message(token, chat_id, text, parsed_text=None, reply_markup=None):
    url = URL(token) + '/sendMessage'
    parameters = {"chat_id": chat_id}
    parameters['text'] = text
    if parsed_text:
        parameters['parse_mode'] = parsed_text
    if reply_markup:
        parameters['reply_markup'] = reply_markup
    return get(url, parameters)

def edit_message(token, chat_id, text, message_id, parsed_text=None, reply_markup=None):
    url = URL(token) + '/editMessageText'
    parameters = {"chat_id": chat_id}
    parameters['text'] = text
    parameters['message_id'] = message_id
    if parsed_text:
        parameters['parse_mode'] = parsed_text
    if reply_markup:
        parameters['reply_markup'] = reply_markup
    return get(url, parameters)

def keyboard_markup(keys):
    markup = {}
    keyboard = []
    for row in keys:
        _row = []
        for key in row:
            _row.append({"text": key})
        keyboard.append(_row)
    markup['keyboard'] = keyboard
    markup['resize_keyboard'] = True

    return json.dumps(markup)

def inline_keyboard_markup(keys):
    markup = {}
    keyboard = []
    for row in keys:
        _row = []
        for key in row:
            _row.append(key)
        keyboard.append(_row)
    markup['inline_keyboard'] = keyboard

    return json.dumps(markup)

def edit_message_caption(token, chat_id, caption, message_id, reply_markup=None):
    url = URL(token) + 'editMessageCaption'
    parameters = {
            'chat_id': chat_id,
            'caption': caption,
            'message_id': message_id,
            'reply_markup': reply_markup
            }
    if reply_markup:
        parameters['reply_markup'] = reply_markup

    return get(url, parameters)


def remove_keyboard_markup():
    return json.dumps({
        "remove_keyboard": True
        })


def break_down(update):
    text = update['message']['text']
    chat_id = update['message']['chat']['id']
    return chat_id, text

def is_text(update):
    return 'text' in update.get('message', {})

def is_start(update):
    return is_text(update) \
            and '/start' in update.get('message',{}).get('text','').lower()

def is_stop(update):
    return is_text(update) \
            and '/stop' in update.get('message',{}).get('text','').lower()

def is_help(update):
    return is_text(update) \
            and '/help' in update.get('message',{}).get('text','').lower()

def is_feedback(update):
    return is_text(update) \
            and '/fb' in update.get('message',{}).get('text','').lower()

def chat_id(update):
    if 'callback_query' in update:
        return update['callback_query']['message']['chat']['id']
    return update['message']['chat']['id']

def text(update):
    return update.get('message', {}).get('text', None)

def main():
    count = 0
    for update in updates():
        if is_text(update):
            chat_id, text = break_down(update)
            print("{}: {}".format(chat_id, text))
            send_message(chat_id, text)

if __name__ == '__main__':
    main()
