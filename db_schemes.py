schemes= [

'''CREATE TABLE reg_users (
    user_id  INTEGER PRIMARY KEY,
    stage    STRING  DEFAULT start,
    new_name STRING  DEFAULT Аноним,
    new_city         DEFAULT NO_CITY,
    city_def INTEGER DEFAULT 0
)''',

'''CREATE TABLE users (
    user_id INTEGER PRIMARY KEY
                    NOT NULL,
    name    STRING,
    city    STRING,
    rating  INTEGER DEFAULT (0),
    stage   STRING  DEFAULT start,
    city_def INTEGER,
    is_user1 INTEGER DEFAULT (0),
    chat_id INTEGER,
    last_partner INTEGER
    
)''',

'''CREATE TABLE queue (
    user_id INTEGER PRIMARY KEY
)''',

'''CREATE TABLE chats (
    chat_id  INTEGER PRIMARY KEY,
    user1_id INTEGER DEFAULT (0),
    user2_id INTEGER DEFAULT (0),
    last_message STRING  
)''']
