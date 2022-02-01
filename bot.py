from vkbottle import API
from vkbottle import Keyboard, KeyboardButtonColor, Text, Location
from vkbottle import PhotoMessageUploader
from vkbottle import VoiceMessageUploader
from vkbottle.dispatch.rules import ABCRule
from vkbottle.bot import Bot, Message

import os
import urllib
import random
import datetime


import config
from database import Database
from config import TEMPPATH as PATH


from opencage.geocoder import OpenCageGeocode
from translate import Translator




def incorrect_name(name):
    if not all(map(str.isalpha, name)):
        return True
    else:
        return False


class HasPhoto(ABCRule[Message]):
    async def check(self, event: Message) ->bool:
        try:
            if (event.attachments[0].photo is not None):
                return True
            else:
                return False
        except:
            return False


class HasVoice(ABCRule[Message]):
    async def check(self, event: Message) ->bool:
        try:
            if (event.attachments[0].audio_message is not None):
                return True
            else:
                return False
        except:
            return False


async def write_message(message, id, keyboard=None):
    await api.messages.send(user_id=id, message=message, keyboard=keyboard, random_id=random.randint(1,999999))


def Generate_keyboard(keyboard_type):
    if(keyboard_type == 'k0'):
        keyboard = Keyboard(one_time=True)
        keyboard.add(Text("Начать"), KeyboardButtonColor.POSITIVE)
        return keyboard

    elif(keyboard_type == "k1"):
        keyboard = Keyboard(one_time=True, inline=False)
        keyboard.add(Text("неважно"))
        return keyboard

    elif(keyboard_type == "k2"):
        keyboard = Keyboard(one_time=True, inline=False)
        keyboard.add(Location())
        keyboard.add(Text("неважно"))
        return keyboard

    elif(keyboard_type == "k3"):
        keyboard = Keyboard(one_time=True, inline=False)
        keyboard.add(Text("Принимаю"))
        return keyboard

    elif(keyboard_type == "k4"):
        keyboard = Keyboard(one_time=True, inline=False)
        keyboard.add(Text("Начать работу"))
        return keyboard

    elif(keyboard_type == "k5"):
        keyboard = Keyboard(one_time=True, inline=False)
        keyboard.add(Text("искать"))
        keyboard.add(Text("анкета"))
        return keyboard

    elif(keyboard_type == 'k6'):
        keyboard = Keyboard(one_time=True, inline=False)
        keyboard.add(Text("Остановить поиск"))
        return keyboard

    elif(keyboard_type == 'k7'):
        keyboard = Keyboard(inline=False, one_time=True)
        keyboard.add(Text("!Стоп"), KeyboardButtonColor.NEGATIVE)
        keyboard.add(Text("!Новый"), KeyboardButtonColor.POSITIVE)
        keyboard.add(Text("!Кто ты?"))
        return keyboard

    elif(keyboard_type == 'k8'):
        keyboard = Keyboard(inline=False, one_time=True)
        keyboard.add(Text("👍🏻"), KeyboardButtonColor.POSITIVE)
        keyboard.add(Text("👎🏻"), KeyboardButtonColor.NEGATIVE)
        return keyboard

    elif(keyboard_type == 'k9'):
        keyboard = Keyboard(one_time=True)
        keyboard.add(Text("Согласиться"), KeyboardButtonColor.PRIMARY)
        return keyboard

    elif(keyboard_type == 'k10'):
        keyboard = Keyboard(one_time=True)
        keyboard.add(Text("!изменить имя"), KeyboardButtonColor.POSITIVE)
        keyboard.row()
        keyboard.add(Text("!изменить город"), KeyboardButtonColor.POSITIVE)
        keyboard.row()
        keyboard.add(Text("!вернуться в меню"), KeyboardButtonColor.PRIMARY)
        return keyboard


bot = Bot(token=config.TOKEN)
api = API(token=config.TOKEN)
db = Database(database_file='data.db')
photo_uploader = PhotoMessageUploader(api)
audio_uploader = VoiceMessageUploader(api)
T = Translator(to_lang="Russian")
Geocoder = OpenCageGeocode(config.OPENCAGETOKEN)


db.init_tables()

print("Server started")


@bot.on.message(HasVoice())
async def bot_send_voice(message: Message):
    users_info = await bot.api.users.get(message.from_id)
    user_id = users_info[0].id
    if(db.get_user_stage(user_id) == "in_chat"):
        mp3_link = message.attachments[0].audio_message.link_mp3
        mp3_id = message.attachments[0].audio_message.id
        urllib.request.urlretrieve(mp3_link, 'C:/Files/Temp/' + str(mp3_id) + '.mp3')
        FileSource = 'C:/Files/Temp/' + str(mp3_id) + '.mp3'
        link = await VoiceMessageUploader(bot.api).upload("new audiomessage", FileSource, peer_id=message.peer_id)

        await api.messages.send(user_id=db.get_partner_id(user_id), message="new voice message", attachment=link, random_id=random.randint(1, 999999), keyboard=Generate_keyboard('k7'))

        folder = 'C:/Files/Temp'
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except:
                pass
    else:
        await bot_message(message)



@bot.on.message(HasPhoto())
async def bot_send_photo(message: Message):
    users_info = await bot.api.users.get(message.from_id)
    user_id = users_info[0].id

    if(db.get_user_stage(user_id) == "in_chat"):

        photos = []
        for photo in message.attachments:
            photo_link = photo.photo.sizes[-1].url
            photo_id = photo.photo.id
            photos.append(photo_link)

            urllib.request.urlretrieve(photo_link, PATH + str(photo_id) + '.jpg')
            FileSource = PATH + str(photo_id) + '.jpg'

            link = await PhotoMessageUploader(bot.api).upload(FileSource)

            await api.messages.send(user_id=db.get_partner_id(user_id), message="new photo", attachment=link,
                                    random_id=random.randint(1, 999999), keyboard=Generate_keyboard('k7'))

            folder = PATH
            for the_file in os.listdir(folder):
                file_path = os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except:
                    pass

    else:
        await bot_message(message)

@bot.on.message(text=['начать', 'Начать'])
async def bot_start(message: Message):
    users_info = await bot.api.users.get(message.from_id)
    user_id = users_info[0].id

    try:
        await write_message(message)
    except:
        msg = "Привет! как мне тебя называть?"
        await write_message(message=msg, id=user_id, keyboard=Generate_keyboard("k1"))
        db.add_reg_user(user_id, 'await_name')


@bot.on.message(text='!Стоп')
async def bot_stop_message(message: Message):
    users_info = await bot.api.users.get(message.from_id)
    user_id = users_info[0].id

    if(db.get_user_stage(user_id) == "in_chat"):
        msg = "Диалог остановлен. Пожалуйста, Оцените вашего собеседника"

        await write_message(msg, user_id, Generate_keyboard("k8"))
        await write_message(msg, db.get_partner_id(user_id), Generate_keyboard("k8"))

        db.user_changestage(user_id, "stop-rating")
        db.user_changestage(db.get_partner_id(user_id), "stop-rating")

        db.quit_from_chat(user_id)

    else:
        await bot_message(message)


@bot.on.message(text='!Новый')
async def bot_next_message(message: Message):
    users_info = await bot.api.users.get(message.from_id)
    user_id = users_info[0].id

    if (db.get_user_stage(user_id) == "in_chat"):
        msg = "Диалог остановлен. Пожалуйста, Оцените вашего собеседника"

        await write_message(msg, user_id, Generate_keyboard("k8"))
        await write_message(msg, db.get_partner_id(user_id), Generate_keyboard("k8"))

        db.user_changestage(user_id, "next-rating")
        db.user_changestage(db.get_partner_id(user_id), "next-rating")


        db.quit_from_chat(user_id)


    else:
        await bot_message(message)


@bot.on.message(text="!Кто ты?")
async def bot_who_message(message: Message):
    users_info = await bot.api.users.get(message.from_id)
    user_id = users_info[0].id

    if(db.get_user_stage(user_id) == 'in_chat'):
        msg = "Вы отправили зпрос на получение страницы вашего собеседника"
        await write_message(msg, user_id, Generate_keyboard('k7'))

        msg = "Ваш Собеседник отправил вам запрос на получение ссылки на вашу страницу"
        await write_message(msg, db.get_partner_id(user_id), Generate_keyboard('k9'))

        db.user_changestage(db.get_partner_id(user_id), "await_who_response")
    else:
        bot_message(message)


@bot.on.message()
async def bot_message(message: Message):
    users_info = await bot.api.users.get(message.from_id)
    user_id = users_info[0].id

    try:
        stage = db.get_user_stage(user_id)
    except:
        try:
            stage = db.get_reg_stage(user_id)
        except:
            db.user_changestage(user_id, 'await_name')
            msg = "Здравствуй! Нажми на кнопку или напиши `начать`, чтобы общаться анонимно"
            await write_message(msg, user_id, Generate_keyboard("k0"))
            stage = "start"



    if(stage == 'await_name'):
        name = message.text
        if (not incorrect_name(name)):
            if (name.lower() != 'неважно'.lower()):
                db.reguser_changename(user_id, name)
            else:
                db.reguser_changename(user_id, 'Аноним')
                name = 'Аноним'

            db.reguser_changename(user_id, name)
            msg = "Приятно познакомиться, "+name+"!\nТеперь введи город"
            await write_message(msg, user_id, Generate_keyboard("k2"))
            db.reguser_changestage(user_id, 'await_city')
        else:
            msg = "Вы ввели что-то неправильное...\nпопробуйте ещё раз"
            await write_message(msg, user_id, Generate_keyboard("k2"))

    elif (stage == "await_city"):
        if (message.geo is not None):
            lat = message.geo.coordinates.latitude
            lon = message.geo.coordinates.longitude

            cityEN = Geocoder.reverse_geocode(lat, lon)[0]['components']['city']
            cityRU = T.translate(cityEN)

            city = cityRU
            msg = "Выбранный город: "+city
            await write_message(msg, user_id, Generate_keyboard('k3'))

        else:
            city = message.text




        if (city.lower() != 'неважно'):
            db.reguser_changecity(user_id, city, 1)
        else:
            db.reguser_changecity(user_id, None, 0)



        msg = "Теперь ознакомьтесь с условиями соглашения:\n"+config.TERMS
        await write_message(msg, user_id, Generate_keyboard('k3'))
        db.reguser_changestage(user_id, "await_terms")

    elif(stage == "await_terms"):
        if (message.text.lower() == "принимаю"):
            db.transmit_user(user_id)
            db.reg_delete(user_id)
            msg = "Прекрасно! Теперь можно начать искать собеседников"
            await write_message(msg, user_id, Generate_keyboard('k4'))
            db.user_changestage(user_id, "main_menu")
        else:
            msg = "пожалуйста, для дальнейшей работы примите условия соглашения"
            await write_message(msg, user_id, Generate_keyboard('k4'))

    elif(stage == "main_menu"):
        msg = "Выберите нужное:\n-искать собеседника\n-моя анкета"
        await write_message(msg, user_id, Generate_keyboard("k5"))
        db.user_changestage(user_id, "menu_choose")

    elif(stage == "menu_choose"):
        if(message.text == "искать"):
            msg = "Поиск собеседника..."
            await write_message(msg, user_id, Generate_keyboard("k6"))
            db.user_changestage(user_id, "in_queue")

            chat = db.cursor.execute("SELECT * FROM 'queue'", ()).fetchmany(1)
            if (bool(len(chat))):
                user_two_id = chat[0][0]
                db.delete_from_queue(user_id)
                db.delete_from_queue(user_two_id)

                db.create_chat(user_id, user_two_id)

                msg = "Найден новый собеседник: <<"+db.get_user_name(user_two_id)+">>\nЧтобы остановить общение, напишите !стоп"
                await write_message(msg, user_id, Generate_keyboard("k7"))
                msg = "Найден новый собеседник: <<" + db.get_user_name(user_id) + ">>\nЧтобы остановить общение, напишите !стоп"
                await write_message(msg, user_two_id, Generate_keyboard("k7"))

                user_city = db.get_user_city(user_id)
                user_two_city = db.get_user_city(user_two_id)

                if(user_city.lower() == user_two_city.lower()):
                    msg = 'С вашим собеседником совпали города'
                    await write_message(user_id, Generate_keyboard('k7'))
                    await write_message(user_two_id, Generate_keyboard('k7'))


                db.user_changestage(user_id, "in_chat")
                db.user_changestage(user_two_id, "in_chat")
                db.make_user_1(user_id)
                db.make_user_0(user_two_id)



            else:
                db.add_to_queue(user_id)


        elif(message.text == "анкета"):
            nickname = db.get_user_name(user_id)
            if(db.get_user_city(user_id) != ""):
                city = db.get_user_city(user_id)
            else:
                city = "скрыт"

            rating = db.get_user_rating(user_id)
            if(rating > 0):
                emoji = "🙂"
            elif(rating < 0):
                emoji = "🙁"
            else:
                emoji = "😐"


            msg1 = "Вот Ваша анкета:\nИмя: "+str(nickname)+"\nГород: "+str(city)+"\nРейтинг: "+str(rating)+emoji

            msg2 = "\n-!изменить имя\n-!изменить город\n-!вернуться в меню"



            msg= msg1+msg2
            await write_message(msg, user_id, Generate_keyboard('k10'))
            db.user_changestage(user_id, "profile_menu_choose")

        else:
            msg = "Выберите нужное:\n-искать собеседника\n-моя анкета"
            await write_message(msg, user_id, Generate_keyboard("k5"))


    elif(stage == "profile_menu_choose"):
        if(message.text == "!изменить имя"):
            msg = "Выберите новое имя"
            await write_message(msg, user_id, Generate_keyboard('k1'))
            db.user_changestage(user_id, 'new_nickname')

        elif(message.text == "!изменить город"):
            msg = "Выберите город"
            await write_message(msg, user_id, Generate_keyboard('k2'))
            db.user_changestage(user_id, "new-city")
        elif(message.text == "!вернуться в меню"):
            await write_message("Выберите нужное:\n-искать собеседника\n-моя анкета", user_id, Generate_keyboard("k5"))
            db.user_changestage(user_id, "menu_choose")


        else:
            msg = "-!изменить имя\n-!изменить город\n-!вернуться в меню"

            await write_message(msg, user_id, Generate_keyboard('k10'))


    elif(stage == 'new-city'):
        if (message.geo is not None):
            lat = message.geo.coordinates.latitude
            lon = message.geo.coordinates.longitude

            cityEN = Geocoder.reverse_geocode(lat, lon)[0]['components']['city']
            cityRU = T.translate(cityEN)

            city = cityRU
            msg = "Выбранный город: "+city
            await write_message(msg, user_id, Generate_keyboard('k3'))

            await write_message("Теперь ваш город: " + city + "\nВыберите нужное:\n-искать собеседника\n-моя анкета",
                                user_id, Generate_keyboard("k5"))
            db.user_changestage(user_id, "menu_choose")
            db.user_changecity(user_id, city)



        elif(message.text != ''):
            await write_message(
                "Теперь ваш город: " + message.text + "\nВыберите нужное:\n-искать собеседника\n-моя анкета",
                user_id, Generate_keyboard("k5"))
            db.user_changestage(user_id, "menu_choose")
            db.user_changecity(user_id, message.text)



        else:
            msg = "Выберите город"
            await write_message(msg, user_id, Generate_keyboard('k2'))




    elif(stage == "new_nickname"):
        name = message.text
        if (not incorrect_name(name)):
            if (name.lower() != 'неважно'.lower()):
                db.user_changename(user_id, name)
            else:
                db.user_changename(user_id, 'Аноним')
                name = 'Аноним'
            await write_message("Теперь ваше имя: " + name + "\nВыберите нужное:\n-искать собеседника\n-моя анкета", user_id,Generate_keyboard("k5"))
            db.user_changestage(user_id, "menu_choose")

        else:
            await write_message("Попробуйте ввести другое имя", user_id, Generate_keyboard('k1'))

    elif(stage == "in_queue"):
        if(message.text == "Остановить поиск"):
            db.delete_from_queue(user_id)
            msg = "Поиск остановлен\nВыберите нужное:\n-искать собеседника\n-моя анкета"
            await write_message(msg, user_id, Generate_keyboard('k5'))
            db.user_changestage(user_id, "menu_choose")

    elif(stage == "in_chat"):

        this_date = datetime.datetime.now()
        last_date = datetime.datetime.fromisoformat(db.get_date(db.get_chat_id(user_id)))
        difference = this_date - last_date

        delta = difference.total_seconds()/60

        if(delta > 10):
            msg = "Диалог остановлен. Пожалуйста, Оцените вашего собеседника"

            await write_message(msg, user_id, Generate_keyboard("k8"))
            await write_message(msg, db.get_partner_id(user_id), Generate_keyboard("k8"))

            db.user_changestage(user_id, "next-rating")
            db.user_changestage(db.get_partner_id(user_id), "next-rating")

            db.quit_from_chat(user_id)

            #выкинуть из чата
        else:
            db.write_date(db.get_chat_id(user_id), this_date)
            if (message.text is not None):
                msg = db.get_user_name(user_id) + ": " + message.text
                await write_message(msg, db.get_partner_id(user_id), Generate_keyboard('k7'))




    elif(stage == "stop-rating"):
        if (message.text == "👍🏻"):
            db.rate_up(db.get_partner_id(user_id))

            msg = "Ваша оценка учтена.\nВыберите нужное:\n-искаь собеседника\n-моя анкета"

            await write_message(msg, user_id, Generate_keyboard('k5'))
            db.user_changestage(user_id, "menu-choose")
            db.quit_from_chat(user_id)


        elif(message.text == "👎🏻"):
            db.rate_down(db.get_partner_id(user_id))
            msg = "Ваша оценка учтена.\nВыберите нужное:\n-искаь собеседника\n-моя анкета"

            await write_message(msg, user_id, Generate_keyboard('k5'))
            db.user_changestage(user_id, "menu-choose")
            db.quit_from_chat(user_id)

    elif (stage == "next-rating"):
        if(message.text == "👍🏻"):
            db.rate_up(db.get_partner_id(user_id))#!!!!!!!!!!!!!!!!!!!!
        elif(message.text == "👎🏻"):
            db.rate_down(db.get_partner_id(user_id))


        msg = "Отлично! продолжаю поиск собеседников"
        await write_message(msg, user_id, Generate_keyboard('k6'))
        db.user_changestage(user_id, "in_queue")

        chat = db.cursor.execute("SELECT * FROM 'queue'", ()).fetchmany(1)
        if (bool(len(chat))):
            user_two_id = chat[0][0]
            db.delete_from_queue(user_id)
            db.delete_from_queue(user_two_id)

            db.create_chat(user_id, user_two_id)

            msg = "Найден новый собеседник: <<" + db.get_user_name(
                user_two_id) + ">>\nЧтобы остановить общение, напишите !стоп"
            await write_message(msg, user_id, Generate_keyboard("k7"))
            msg = "Найден новый собеседник: <<" + db.get_user_name(
                user_id) + ">>\nЧтобы остановить общение, напишите !стоп"
            await write_message(msg, user_two_id, Generate_keyboard("k7"))

            db.user_changestage(user_id, "in_chat")
            db.user_changestage(user_two_id, "in_chat")
            db.make_user_1(user_id)
            db.make_user_0(user_two_id)

        else:
            db.add_to_queue(user_id)

    elif (stage == "await_who_response"):
        if(message.text.lower() == "согласиться"):
            msg = "Вы передали информацию о вас собеседнику"
            await write_message(msg, user_id, Generate_keyboard('k7'))

            msg = "Ваш собеседник согласился передать о себе информацию\nСсылка: https://vk.com/id"+str(user_id)
            await write_message(msg, db.get_partner_id(user_id), Generate_keyboard('k7'))

            db.user_changestage(user_id, "in_chat")
        else:
            msg = "Ваш собеседник не согласился передать о себе информацию"
            await write_message(msg, db.get_partner_id(user_id))
            db.user_changestage(user_id, "in_chat")


bot.run_forever()
