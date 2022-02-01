import sqlite3
import db_schemes
import datetime as dt


class Database:
    def __init__(self, database_file):
        self.connection = sqlite3.connect(database_file, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def init_tables(self):

        for scheme in db_schemes.schemes:
            try:
                self.cursor.execute(scheme)
            except:
                pass


    def add_reg_user(self, user_id, stage):
        self.cursor.execute("INSERT OR IGNORE INTO reg_users (user_id, stage) VALUES (?, ?)", (user_id, stage))

    def reguser_changestage(self, user_id, stage):
        self.cursor.execute("UPDATE reg_users SET stage = ? WHERE user_id = ?", (stage, user_id))

    def get_reg_stage(self, user_id):
        info = self.cursor.execute("SELECT stage FROM reg_users WHERE user_id = ?", (user_id,)).fetchmany(1)
        a = info[0][0]
        return a

    def reguser_changename(self, user_id, name):
        self.cursor.execute("UPDATE reg_users SET new_name = ? WHERE user_id = ?", (name, user_id))

    def reguser_changecity(self, user_id, city, is_defined):
        self.cursor.execute("UPDATE reg_users SET new_city = ? WHERE user_id = ?", (city, user_id))
        self.cursor.execute("UPDATE reg_users SET city_def = ? WHERE user_id = ?", (is_defined, user_id))


    def transmit_user(self, user_id):
        info = self.cursor.execute("SELECT * FROM reg_users WHERE user_id = ?", (user_id,)).fetchmany(1)
        name = info[0][2]
        city = info[0][3]
        stage = info[0][1]
        city_defined = info[0][4]
        self.cursor.execute("INSERT OR IGNORE INTO users (user_id, name, city, stage, city_def) VALUES (?, ?, ?,?,?)", (user_id, name, city, stage, city_defined))

    def reg_delete(self, user_id):
        self.cursor.execute("DELETE FROM reg_users WHERE user_id = ?", (user_id,))

    def add_to_queue(self, user_id):
        self.cursor.execute("INSERT OR IGNORE INTO queue (user_id) VALUES (?)", (user_id,))


    def delete_from_queue(self, user_id):
        self.cursor.execute("DELETE FROM queue WHERE user_id = ?", (user_id,))

    def user_changename(self, user_id, name):
        self.cursor.execute("UPDATE users SET name = ? WHERE user_id = ?", (name, user_id))

    def user_changestage(self, user_id, stage):
        self.cursor.execute("UPDATE users SET stage = ? WHERE user_id = ?", (stage, user_id))

    def user_changechat(self, user_id, chat_id):
        self.cursor.execute("UPDATE users SET chat_id = ? WHERE user_id = ?", (chat_id, user_id,))

    def user_changecity(self, user_id, city):
        self.cursor.execute("UPDATE users SET city = ? WHERE user_id = ?", (city, user_id,))


    def get_user_stage(self,user_id):
        info = self.cursor.execute("SELECT stage FROM users WHERE user_id = ?", (user_id,)).fetchmany(1)
        return info[0][0]

    def get_user_name(self, user_id):
        info = self.cursor.execute("SELECT name FROM users WHERE user_id = ?", (user_id,)).fetchmany(1)
        return info[0][0]

    def get_user_city(self, user_id):
        info = self.cursor.execute("SELECT city FROM users WHERE user_id = ?", (user_id,)).fetchmany(1)
        return info[0][0]

    def get_user_rating(self, user_id):
        info = self.cursor.execute("SELECT rating FROM users WHERE user_id = ?", (user_id,)).fetchmany(1)
        return info[0][0]




    def create_chat(self, user1_id, user2_id):
        self.cursor.execute("INSERT INTO chats (user1_id, user2_id) VALUES (?,?)", (user1_id, user2_id))
        self.cursor.execute("UPDATE users SET last_partner = ? WHERE user_id = (?)", (user1_id, user2_id))
        self.cursor.execute("UPDATE users SET last_partner = ? WHERE user_id = (?)", (user2_id, user1_id))


    def make_user_1(self, user_id):
        self.cursor.execute("UPDATE users SET is_user1 = (1) WHERE user_id = (?)", (user_id,))

    def make_user_0(self, user_id):
        self.cursor.execute("UPDATE users SET is_user1 = 0 WHERE user_id = (?)", (user_id,))

    def get_chat_id(self, user_id):
        info = self.cursor.execute("SELECT chat_id FROM users WHERE user_id = (?)", (user_id,)).fetchmany(1)
        return info[0][0]

    def quit_from_chat(self, user_id):
        partner = self.get_partner_id(user_id)
        if (partner != 0):
            if(self.is_user_1(user_id) == 1):
                self.cursor.execute("DELETE user1_id FROM chats WHERE chat_id = ?", (self.get_chat_id(user_id),))
            else:
                self.cursor.execute("DELETE user2_id FROM chats WHERE chat_id = ?", (self.get_chat_id(user_id),))

        else:
            self.cursor.execute("DELETE FROM chats WHERE chat_id = ?", (self.get_chat_id(user_id),))



    def get_partner_id(self, user_id):
        try:
            chat_id = self.get_chat_id(user_id)
            if (self.is_user_1(user_id)):
                return self.cursor.execute("SELECT user2_id FROM chats WHERE chat_id = ?", (chat_id,)).fetchmany(1)[0][0]
            else:
                return self.cursor.execute("SELECT user1_id FROM chats WHERE chat_id = ?", (chat_id,)).fetchmany(1)[0][0]
        except:
            return self.cursor.execute("SELECT last_partner FROM users WHERE user_id = ?", (user_id,)).fetchmany(1)[0][0]


    def is_user_1(self, user_id):
        info = self.cursor.execute("SELECT is_user1 FROM users WHERE user_id = (?)", (user_id,)).fetchmany(1)
        if(info[0][0] == 1):
            return True
        else:
            return False

    def rate_up(self, user_id):
        info = self.cursor.execute("SELECT rating FROM users WHERE user_id = (?)", (user_id,)).fetchmany(1)
        old_rating = info[0][0]
        new_rating = old_rating + 1
        self.cursor.execute("UPDATE users SET rating = ? WHERE user_id = ?", (new_rating, user_id,))

    def rate_down(self, user_id):
        info = self.cursor.execute("SELECT rating FROM users WHERE user_id = (?)", (user_id,)).fetchmany(1)
        old_rating = info[0][0]
        new_rating = old_rating - 1
        self.cursor.execute("UPDATE users SET rating = ? WHERE user_id = ?", (new_rating, user_id,))

    def write_date(self, chat_id, d):

        date_string = d.isoformat(sep=' ')[:19]
        self.cursor.execute("UPDATE chats SET last_message = ? WHERE chat_id = ?", (date_string, chat_id))

    def get_date(self, chat_id):
        try:
            date = self.cursor.execute("SELECT last_message FROM chats WHERE chat_id=?", (chat_id,))
            date_string = dt.datetime.fromtimestamp(date)

            return date_string.isoformat(sep=' ')[:19]

        except:

            date_string= dt.datetime.now()
            return date_string.isoformat(sep=' ')[:19]


    def a(self, user_id):
        M = self.cursor.execute("SELECT * FROM reg_users").fetchmany(1)
        pass