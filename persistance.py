import sqlite3

class SQlite:

    def __init__(self, db='subs.sqlite'):
        self.dbname = db
        self.conn = sqlite3.connect(db)
        self.setup()

    def setup(self):
        volume_change_table = "CREATE TABLE IF NOT EXISTS volume_change (token text, chat_id text, increase real, decrease real, subscribed integer)"
        feedback_table = "CREATE TABLE IF NOT EXISTS fb (chat_id text, feedback text)"
        users_table = "CREATE TABLE IF NOT EXISTS users (token text, chat_id text)"
        bots_table = "CREATE TABLE IF NOT EXISTS bots (token text, bot_username, count integer)"
        users_bots_table = "CREATE TABLE IF NOT EXISTS users_bots (token text, bot_username text, chat_id text)"
        self.conn.execute(volume_change_table)
        self.conn.execute(feedback_table)
        self.conn.execute(users_table)
        self.conn.execute(bots_table)
        self.conn.execute(users_bots_table)
        self.conn.commit()

    def all_bots(self):
        stmt = "SELECT token FROM bots"
        return [x[0] for x in self.conn.execute(stmt)]

    def first_time(self, token, chat_id):
        stmt = "SELECT token, chat_id FROM users where token = (?) and chat_id = (?)"
        return len(list(self.conn.execute(stmt, (token, chat_id)))) == 0

    def bot_by_token(self, token):
        stmt = "SELECT token, bot_username FROM bots where token = (?)"
        results = list(self.conn.execute(stmt, (token,)))
        return results[0]


    def attach_bot(self, token, bot_username, chat_id):
        stmt = "INSERT INTO users_bots (token, bot_username, chat_id) VALUES (?, ?, ?)"
        args = (token, bot_username, str(chat_id))
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_attached_bot(self, chat_id):
        stmt = "SELECT token, bot_username FROM users_bots where chat_id = (?)"
        results = list(self.conn.execute(stmt, (chat_id,)))
        return results[0]

    def add_bot(self, token, bot_username, count=0):
        stmt = "INSERT INTO bots (token, bot_username, count) VALUES (?, ?, ?)"
        args = (token, bot_username, count)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def select_bot(self):
        stmt = "SELECT token, bot_username, count FROM bots where count < 50 ORDER BY count DESC"
        results = list(self.conn.execute(stmt))
        token, bot_username, count = results[0]
        stmt = "UPDATE bots SET count = (?) WHERE token = (?)"
        self.conn.execute(stmt, (count + 1, token))
        self.conn.commit()
        return token, bot_username

    def add_chat_id(self, chat_id):
        stmt = "INSERT INTO volume_updates (chat_id) VALUES (?)"
        args = (chat_id,)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_chat_id(self, chat_id):
        stmt = "DELETE FROM volume_updates where chat_id = (?)"
        args = (chat_id,)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def add_feedback(self, chat_id, feedback):
        stmt = "INSERT INTO fb (chat_id, feedback) VALUES (?, ?)"
        args = (chat_id, feedback)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_feedbacks(self):
        stmt = "SELECT chat_id, feedback from fb"
        return [(x[0], x[1]) for x in self.conn.execute(stmt)]


    def get_chat_ids(self):
        stmt = "SELECT DISTINCT chat_id FROM volume_updates"
        return [x[0] for x in self.conn.execute(stmt)]


    def start(self, token, chat_id):
        stmt = "SELECT chat_id, token from users where chat_id = (?) and token = (?)"
        results = self.conn.execute(stmt, (chat_id, token))
        if len(list(results)) == 0:
            stmt = "INSERT INTO users (token, chat_id) VALUES (?, ?)"
            self.conn.execute(stmt, (token, chat_id))
            self.conn.commit()
        stmt = "UPDATE volume_change SET subscribed = 1 where token = (?) and chat_id = (?)"
        self.conn.execute(stmt, (token, chat_id))
        self.conn.commit()

    def stop(self, token, chat_id):
        stmt = "UPDATE volume_change SET subscribed = 0 where token = (?) and chat_id = (?)"
        self.conn.execute(stmt, (token, chat_id))
        self.conn.commit()

    def set_volume(self, token, chat_id, increase=None, decrease=None):
        stmt = "SELECT chat_id, token from volume_change where chat_id = (?) and token = (?)"
        results = self.conn.execute(stmt, (chat_id, token))
        if len(list(results)) == 0:
            stmt = "INSERT INTO volume_change (token, chat_id, increase, decrease, subscribed) VALUES (?, ?, ?, ?, ?)"
            self.conn.execute(stmt, (token, chat_id, increase, decrease, 1))
            self.conn.commit()
        else:
            stmt = "UPDATE volume_change SET increase = (?), decrease = (?)  where token = (?) and chat_id = (?)"
            self.conn.execute(stmt, (increase, decrease, token, chat_id))
            self.conn.commit()

    def get_volumes(self):
        stmt = "SELECT token, chat_id, increase, decrease, subscribed FROM volume_change where subscribed = 1"
        return list(self.conn.execute(stmt))
