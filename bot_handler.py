from pprint import pprint
import persistance
import json
from samtar import telegram
#import dev_config as config
import config
import telegram_incoming as tgi
import telegram_outgoing as tgo
import zmq
import zmq_utils

chat_id = telegram.chat_id
text = telegram.text

def has_text(update, txt):
    return text(update) and txt in text(update).lower()

def is_start(update):
    return has_text(update, '/start')

def is_stop(update):
    return has_text(update, '/stop')

def is_help(update):
    return has_text(update, '/help')

def is_set_volume(update):
    return has_text(update, '/vol')

def is_feedback(update):
    return has_text(update, '/fb')

def is_cancel(update):
    return has_text(update, '/cancel')

def is_my_bot(update):
    return has_text(update, '/my_bot')

def on_update(socket, token):
    sqlite = persistance.SQlite(config.db_file)
    while True:
        update = yield
        pprint(update)
        if token == config.main_bot_token:
            if sqlite.first_time(token, chat_id(update)):
                tgo.send_message(socket, token, chat_id(update), "Welcome to Nemesis")
                bot_token, bot_username = sqlite.select_bot()
                sqlite.attach_bot(bot_token, bot_username, chat_id(update))
                sqlite.start(token, chat_id(update))
                tgo.send_message(socket, token, chat_id(update), "Hi.\nThis is our primary bot, handling all the updates and announcements about the bot and changes in it.\n For signals join your personal bot.", 'Markdown')
            if is_start(update):
                bot_token, bot_username = sqlite.get_attached_bot(chat_id(update))
                kb =  {"inline_keyboard":[[{"text":"Nemesis Personal Signals", "url":"t.me/{}".format(bot_username)}]]}
                tgo.send_message(socket, token, chat_id(update), "Please join your personal bot.", 'Markdown', json.dumps(kb))
            elif is_my_bot(update):
                bot_token, bot_username = sqlite.get_attached_bot(chat_id(update))
                tgo.send_message(socket, token, chat_id(update), "Please join [Nemesis Personal Signals](t.me/{})".format(bot_username), 'Markdown')
            elif is_help(update):
                tgo.send_message(socket, token, chat_id(update), "send /my_bot to get your personal signals bot");
            continue

        if is_start(update):
            sqlite.start(token, chat_id(update))
            tgo.send_message(socket, token, chat_id(update), "You are welcome, send /volume to set your threshold")
            continue
        if is_stop(update):
            print(list(sqlite.get_volumes()))
            sqlite.stop(token, chat_id(update))
            tgo.send_message(socket, token, chat_id(update), "You will not recieve any more updates");
            continue
        if is_help(update):
            tgo.send_message(socket, token, chat_id(update), "send /start to start\nsend /stop to stop getting update\nsend /volume to set volume threshold");
            continue
        if is_set_volume(update):
            #if alreay set send the values and ask to change if needed
            _text = text(update)
            try:
                percentage = _text.split()
                print(percentage)
                percentage = percentage[1]
            except IndexError:
                percentage = None
            print(_text)
            if percentage and percentage.isnumeric():
                percentage = float(percentage)
                if percentage < 10:
                    tgo.send_message(socket, token, chat_id(update), "Enter a number greater than 10")
                else:
                    sqlite.set_volume(token, chat_id(update), increase=float(percentage), decrease=float(percentage))
                    tgo.send_message(socket, token, chat_id(update), "Theshold set at {}".format(percentage))
                continue

            tgo.send_message(socket, token, chat_id(update), "send value in percentage for which you want notifications for.\nIf you wish to cancel this operation send /cancel", "Markdown")
            update = yield
            while not is_cancel(update):
                percentage = text(update)
                if percentage and percentage.isnumeric() and float(percentage) >=10:
                    sqlite.set_volume(token, chat_id(update), increase=float(percentage), decrease=float(percentage))
                    print(sqlite.get_volumes())
                    tgo.send_message(socket, token, chat_id(update), "Theshold set at {}".format(percentage))
                    break
                else:
                    tgo.send_message(socket, token, chat_id(update), "Enter a number greater than 10")
                    tgo.send_message(socket, token, chat_id(update), "send /cancel to cancel current operation");
                update = yield
            continue
        if is_feedback(update):
            #take feedback
            continue


def main():
    handlers = {}
    socket = zmq_utils.create_socket(zmq.PUB, config.telegram_outgoing_pub_port, False)
    for token, update in tgi.all_updates():
        if chat_id(update) == None:
            continue
        if (chat_id(update), token) not in handlers:
            handlers[(chat_id(update), token)] = on_update(socket, token)
            handlers[(chat_id(update), token)].send(None)
        handlers[(chat_id(update), token)].send(update)

if __name__ == '__main__':
    main()
