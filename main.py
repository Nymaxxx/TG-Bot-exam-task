# -*- coding: utf8 -*-
import telebot
from telebot import types
from config import *
import json
import backend


bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    backend.create_user(message.from_user.username, message.chat.id)

    if backend.get_status(message.from_user.username) == '1':
        bot.send_message(message.chat.id, f'Добро пожаловать, {message.from_user.first_name}!', reply_markup=menu_keyboard())
        bot.send_message(message.chat.id, "Напоминаю:\n\n" + hlp, parse_mode="Markdown")
        bot.register_next_step_handler(message, menu)

    elif backend.get_status(message.from_user.username) == '0':
        bot.send_message(message.chat.id, f'Добро пожаловать, {message.from_user.first_name}!\n\nДля начала заполните профиль, чтобы мы могли подобрать вакансии для вас!', reply_markup=set_profile())



@bot.message_handler(content_types=["text"])
def step0(message):
    if message.text == 'Заполнить профиль!':
        step1_filling_0(message)


# Алгоритм заполнения профиля
def step1_filling_0(message): #step_0
    bot.send_message(message.chat.id, 'Выберите сферы работы:', reply_markup=choose_job(message))
    bot.register_next_step_handler(message, step1_filling_1)


def step1_filling_1(message): #step1
    if message.text == 'Software Development' or message.text == '✅ Software Development':
        bot.send_message(message.chat.id, 'Выберите сферу разработки:', reply_markup=choose_soft(message))
        bot.register_next_step_handler(message, step1_filling_2)

    elif (message.text != 'Готово') and (message.text != 'Software Development' or message.text != '✅ Software Development') and ((message.text in jobs) or (message.text in jobs_checked)):
        data = backend.get_sphere(message.from_user.username)
        #print(data)
        result = list(data)
        st = ''
        for j in range(len(jobs)):
            if message.text == jobs[j]:
                if result[j] == '0':
                    result[j] = '1'
                for i in range(len(result)):
                    st += result[i]
                #print(st)
                backend.update_sphere(message.from_user.username, st)
                bot.send_message(message.chat.id, 'Добавлено', reply_markup=choose_job(message))

            elif message.text == '✅ ' + jobs[j]:
                if result[j] == '1':
                    result[j] = '0'

                for i in range(len(result)):
                    st += result[i]
                #print(st)
                backend.update_sphere(message.from_user.username, st)
                bot.send_message(message.chat.id, 'Убрано', reply_markup=choose_job(message))

        bot.register_next_step_handler(message, step1_filling_1)

    elif message.text == 'Готово':
        if backend.get_status(message.from_user.username) == '0':
            step5_exp_0(message)

        elif backend.get_status(message.from_user.username) == '1':
            bot.send_message(message.chat.id, 'Вы успешно выбрали направления!', reply_markup=update_profile(message))
            bot.register_next_step_handler(message, update)
    else:
        bot.register_next_step_handler(message, step1_filling_1)


def step1_filling_2(message): #step11
    if message.text == 'Назад':
        step1_filling_0(message)

    elif (message.text in softs) or (message.text in softs_checked):
        data = backend.get_sphere1(message.from_user.username)
        result = list(data)
        st = ''
        for j in range(len(softs)):
            if message.text == softs[j]:
                if result[j] == '0':
                    result[j] = '1'
                for i in range(len(result)):
                    st += result[i]

                backend.update_sphere1(message.from_user.username, st)
                bot.send_message(message.chat.id, 'Добавлено', reply_markup=choose_soft(message))


            elif message.text == '✅ ' + softs[j]:
                if result[j] == '1':
                    result[j] = '0'

                for i in range(len(result)):
                    st += result[i]

                backend.update_sphere1(message.from_user.username, st)
                bot.send_message(message.chat.id, 'Убрано', reply_markup=choose_soft(message))


        bot.register_next_step_handler(message, step1_filling_2)

    else:
        bot.register_next_step_handler(message, step1_filling_2)



def step5_exp_0(message): #step_7
    bot.send_message(message.chat.id, 'Введите ваш опыт работы:', reply_markup=level())
    bot.register_next_step_handler(message, step5_exp_1)


def step5_exp_1(message): #step_8
    level = message.text
    if level not in ["No experience", "Junior", "Middle", "Senior", "Teamlead"]:
        bot.register_next_step_handler(message, step5_exp_1)
    else:
        if backend.get_status(message.from_user.username) == '0':
            backend.update_level(message.from_user.username, level)
            step3_format_0(message)

        else:
            backend.update_level(message.from_user.username, level)
            bot.send_message(message.chat.id, 'Успешно!', reply_markup=update_profile(message))
            bot.register_next_step_handler(message, update)


def step3_format_0(message): #step_format1
    bot.send_message(message.chat.id, 'Выберите формат работы:', reply_markup=format())
    bot.register_next_step_handler(message, step3_format_1)


def step3_format_1(message): #step_format2
    format = message.text
    if format not in ["Office", "Remote","Hybrid"]:
        bot.register_next_step_handler(message, step3_format_1)
    else:
        backend.update_format(message.from_user.username, format)
        if backend.get_status(message.from_user.username) == '0':
            backend.update_status(message.from_user.username)
            bot.send_message(message.chat.id, 'Вы успешно заполнили профиль!', reply_markup=menu_keyboard())
            bot.send_message(message.chat.id, hlp, parse_mode="Markdown")
            bot.register_next_step_handler(message, menu)

        else:
            bot.send_message(message.chat.id, 'Успешно!', reply_markup=update_profile(message))
            bot.register_next_step_handler(message, update)




# Menu
def menu(message):
    if message.text == 'Подобрать для меня':
        bot.send_message(message.chat.id, "Пожалуйста, подождите, идет поиск...", parse_mode="Markdown")

        if len(backend.vac_for_me(message.from_user.username)) == 0:
            bot.send_message(message.chat.id, 'Для Вас вакансий пока нет :(\nПопробуйте поменять параметры профиля или посмотреть все вакансии в разделе *Посмотреть все*!', parse_mode="Markdown", reply_markup=menu_keyboard())
            bot.register_next_step_handler(message, menu)

        elif len(backend.vac_for_me(message.from_user.username)) > 0:
             bot.send_message(message.chat.id, f'Найдено подходящих вакансий: {len(backend.vac_for_me(message.from_user.username))}', reply_markup=look_through())
             bot.register_next_step_handler(message, search_for_me_0)

    elif message.text == 'Посмотреть все':
        bot.send_message(message.chat.id, f'Всего вакансий: {backend.vac_number(backend.more())}', reply_markup=look_through())
        bot.register_next_step_handler(message, search_vac_0)

    elif message.text == 'Обновить профиль':
        bot.send_message(message.chat.id, 'Обновляем профиль!', reply_markup=update_profile(message))
        bot.register_next_step_handler(message, update)

    elif message.text == 'Помощь':
        btn1 = types.InlineKeyboardButton(text='Связаться с техподдержкой', url='https://t.me/techh_bot_support', callback_data='click1')
        btn2 = types.InlineKeyboardButton(text='Не могу найти вакансию!', callback_data='click2.' + str(message.from_user.username))
        markup = types.InlineKeyboardMarkup().add(btn1).add(btn2)
        bot.send_message(message.chat.id, 'Нажмите на одну из кнопок ниже, чтобы связаться с поддержкой', reply_markup=markup)
        bot.register_next_step_handler(message, menu)

    elif message.text == 'Мои отклики':
        vcs = backend.get_vacancies(message.from_user.username, 0)

        if vcs != None:
            bot.send_message(message.chat.id, 'Вы подались на следующие вакансии:')
            bot.send_message(message.chat.id, vcs, parse_mode="Markdown", reply_markup=otkliki_markup())
            #bot.send_message(message.chat.id, "*Важно:* для отклика вам самостоятельно нужно написать указанному в вакансии контакту", parse_mode="Markdown")
            bot.register_next_step_handler(message, otkliki)
        else:
            bot.send_message(message.chat.id, 'Вы не подались ни на одну вакансию!')
            bot.register_next_step_handler(message, menu)

    elif message.text == 'FAQ':

        btn1 = types.InlineKeyboardButton(text='1. Плюсы и минусы стартапов и IT-гигантов', url='https://habr.com/ru/company/gms/blog/532752/', callback_data='click3')
        btn2 = types.InlineKeyboardButton(text='2. Советы по удаленке разработчиков разных стран', url='https://habr.com/ru/company/gms/blog/586246/', callback_data='click4')
        btn3 = types.InlineKeyboardButton(text='3. Плюсы и минусы разных ІТ-компаний', url='https://dou.ua/lenta/columns/pros-and-cons-of-different-companies/', callback_data='click5')
        btn4 = types.InlineKeyboardButton(text='4. Онлайн-сервис для поиска вакансий в стартапах', url='https://cofoundit.ru/', callback_data='click6')
        markup = types.InlineKeyboardMarkup().add(btn1).add(btn2).add(btn3).add(btn4)
        bot.send_message(message.chat.id, "Собрали для вас подборку материалов, рекомендаций и источников, которые могут быть полезны при выборе работы в IT:", parse_mode="Markdown", reply_markup=markup)
        bot.register_next_step_handler(message, menu)


    else:
        bot.register_next_step_handler(message, menu)



# Мои отклики
def otkliki(message):
    if message.text == "Удалить отклик":
        bot.send_message(message.chat.id, "Введите номер отклика, который хотите удалить:")
        bot.register_next_step_handler(message, otkliki_delete)

    elif message.text == "Назад":
        bot.send_message(message.chat.id, "Возвращаемся в меню!", reply_markup=menu_keyboard())
        bot.register_next_step_handler(message, menu)
    else:
        bot.register_next_step_handler(message, otkliki)



# Обновление профиля
def update(message):
    data = backend.get_sphere(message.from_user.username)
    result = list(data)
    data1 = backend.get_sphere1(message.from_user.username)
    result1 = list(data1)
    sphere_count = 0
    for i in range(len(result)):
        sphere_count += int(result[i])
    for i in range(len(result1)):
        sphere_count += int(result1[i])

    level = backend.get_level(message.from_user.username)
    format = backend.get_format(message.from_user.username)

    if message.text == f'Сфера [Выбрано: {sphere_count}]':
        step1_filling_0(message)
    elif message.text == f'Опыт [{level}]':
        step5_exp_0(message)
    elif message.text == f'Формат [{format}]':
        step3_format_0(message)
    elif message.text == 'Завершить ✅':
        bot.send_message(message.chat.id, 'Профиль обновлен', reply_markup=menu_keyboard())
        bot.register_next_step_handler(message, menu)
    else:
        bot.register_next_step_handler(message, update)



#Показать вакансии для меня
def search_for_me_0(message):
    if message.text == 'Посмотреть!':
        search_for_me_1(message, 0)
    else:
        bot.register_next_step_handler(message, search_for_me_0)

def search_for_me_1(message, i, flag = 0):
    rows = backend.vac_for_me(message.from_user.username)

    if message.text == 'Откликнуться':
        bot.send_message(message.chat.id, 'Спасибо за ваш отклик!\nВсе отклики вы можете отслеживать в основном меню.\n\nДля отклика по данной вакансии Вам необходимо обратиться по адресу:\n\n' + str(backend.fmore(rows[i])), parse_mode="Markdown")
        backend.update_vcs(message.from_user.username, rows[i])
        bot.register_next_step_handler(message, search_for_me_1, i)

    elif message.text == 'Меню':
        bot.send_message(message.chat.id, 'Возвращаемся в меню', reply_markup=menu_keyboard())
        bot.register_next_step_handler(message, menu)

    elif len(rows) == 1 and (message.text in ["Откликнуться", "Назад", "Вперед", "Меню", "Посмотреть!"]):
        if flag == 0:
            text = backend.card(rows[i])
            flag += 1
            bot.send_message(message.chat.id, text, reply_markup=vac(), parse_mode="Markdown")
            bot.send_message(message.chat.id, "Это единственная подходящая вакансия!")
            bot.register_next_step_handler(message, search_for_me_1, i, 1)
        elif flag == 1:
            bot.send_message(message.chat.id, "Это единственная подходящая вакансия!")
            bot.register_next_step_handler(message, search_for_me_1, i, 1)


    elif message.text == 'Назад' and i > 0:
        i -= 1
        text = backend.card(rows[i])
        bot.send_message(message.chat.id, text, reply_markup=vac(), parse_mode="Markdown")
        if i == 0:
            bot.send_message(message.chat.id, "Это первая вакансия в списке!")
        bot.register_next_step_handler(message, search_for_me_1, i)

    elif message.text == 'Назад' and i == 0:
        bot.send_message(message.chat.id, "Это первая вакансия в списке!")
        bot.register_next_step_handler(message, search_for_me_1, i)

    elif message.text == 'Вперед' and i < len(rows) - 1:
        i += 1
        text = backend.card(rows[i])
        bot.send_message(message.chat.id, text, reply_markup=vac(), parse_mode="Markdown")
        if i == len(rows) - 1:
            bot.send_message(message.chat.id, "Это последняя вакансия в списке!")
        bot.register_next_step_handler(message, search_for_me_1, i)

    elif i == len(rows) - 1 and (message.text in ["Откликнуться", "Назад", "Вперед", "Меню", "Посмотреть!"]):
        bot.send_message(message.chat.id, "Это последняя вакансия в списке!")
        bot.register_next_step_handler(message, search_for_me_1, i)

    elif message.text not in ["Откликнуться", "Назад", "Вперед", "Меню", "Посмотреть!"]:
        bot.register_next_step_handler(message, search_for_me_1, i)

    elif (0 <= i <= len(rows)) and (len(rows) > 1):
        text = backend.card(rows[i])
        bot.send_message(message.chat.id, text, reply_markup=vac(), parse_mode="Markdown")
        bot.register_next_step_handler(message, search_for_me_1, i)

    else:
        print("Часть 2")
        bot.register_next_step_handler(message, search_for_me_1, i)





#Посмотреть все вакансии
def search_vac_0(message):
   if message.text == 'Посмотреть!':
        search_vac_1(message, 0)
   else:
       bot.register_next_step_handler(message, search_vac_0)

def search_vac_1(message, i):
    #if message.text == 'Назад' or message.text == 'Вперед':
    #    bot.delete_message(message.chat.id, message.message_id-1)
    #    bot.delete_message(message.chat.id, message.message_id)

    if message.text == 'Откликнуться':
        bot.send_message(message.chat.id, 'Спасибо за ваш отклик!\nВсе отклики вы можете отслеживать в основном меню.\n\nДля отклика по данной вакансии Вам необходимо обратиться по адресу:\n\n' + str(backend.fmore(i)), parse_mode="Markdown")
        backend.update_vcs(message.from_user.username, i)
        bot.register_next_step_handler(message, search_vac_1, i)

    elif message.text == 'Меню':
        bot.send_message(message.chat.id, 'Возвращаемся в меню', reply_markup=menu_keyboard())
        bot.register_next_step_handler(message, menu)


    elif message.text == 'Назад' and i > 0:
        i -= 1
        text = backend.card(i)
        bot.send_message(message.chat.id, text, reply_markup=vac(), parse_mode="Markdown")
        if i == 0:
            bot.send_message(message.chat.id, "Это первая вакансия в списке!")
        bot.register_next_step_handler(message, search_vac_1, i)

    elif message.text == 'Назад' and i == 0:
        bot.send_message(message.chat.id, "Это первая вакансия в списке!")
        bot.register_next_step_handler(message, search_vac_1, i)


    elif message.text == 'Вперед' and i < backend.vac_number(backend.more()) - 1:
        i += 1
        text = backend.card(i)
        bot.send_message(message.chat.id, text, reply_markup=vac(), parse_mode="Markdown")
        if i == backend.vac_number(backend.more()) - 1:
            bot.send_message(message.chat.id, "Это последняя вакансия в списке!")
        bot.register_next_step_handler(message, search_vac_1, i)

    elif i == backend.vac_number(backend.more()) - 1 and (message.text in ["Откликнуться", "Назад", "Вперед", "Меню", "Посмотреть!"]):
        bot.send_message(message.chat.id, "Это последняя вакансия в списке!")
        bot.register_next_step_handler(message, search_vac_1, i)

    elif message.text not in ["Откликнуться", "Назад", "Вперед", "Меню", "Посмотреть!"]:
        bot.register_next_step_handler(message, search_vac_1, i)

    else:
        text = backend.card(i)
        bot.send_message(message.chat.id, text, reply_markup=vac(), parse_mode="Markdown")
        bot.register_next_step_handler(message, search_vac_1, i)


# Заглушка
def echo(message):
    pass


@bot.callback_query_handler(func=lambda call: call.data.split('.')[0] == "click2")
def handle2(call):
    bot.send_message(call.message.chat.id, "\nРасскажите нам, что Вы не смогли найти, чтобы мы попробовали это исправить: *@techh_bot_support*", parse_mode="Markdown", reply_markup=menu_keyboard())
    backend.not_f(call.data.split('.')[1])
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda message: True)
def set_profile():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Заполнить профиль!')
    markup.add(btn1)
    return markup

def update_profile(message):
    data = backend.get_sphere(message.from_user.username)
    result = list(data)
    data1 = backend.get_sphere1(message.from_user.username)
    result1 = list(data1)
    sphere_count = 0
    for i in range(len(result)):
        sphere_count += int(result[i])
    for i in range(len(result1)):
        sphere_count += int(result1[i])

    level = backend.get_level(message.from_user.username)
    format = backend.get_format(message.from_user.username)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(f'Сфера [Выбрано: {sphere_count}]')
    btn2 = types.KeyboardButton(f'Опыт [{level}]')
    btn3 = types.KeyboardButton(f'Формат [{format}]')
    btn4 = types.KeyboardButton('Завершить ✅')
    markup.add(btn1).add(btn2).add(btn3).add(btn4)
    return markup

def menu_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True) #, one_time_keyboard=True)
    btn1 = types.KeyboardButton('Подобрать для меня')
    btn2 = types.KeyboardButton('FAQ')
    btn3 = types.KeyboardButton('Посмотреть все')
    btn4 = types.KeyboardButton('Обновить профиль')
    btn5 = types.KeyboardButton('Мои отклики')
    btn6 = types.KeyboardButton('Помощь')
    markup.add(btn1, btn2).add(btn3, btn4).add(btn5, btn6)
    return markup

def choose_job(message):
    data = backend.get_sphere(message.from_user.username)
    result = list(data)
    data_soft = backend.get_sphere1(message.from_user.username)
    result_soft = list(data_soft)
    sum_soft = 0

    for i in range(len(result_soft)):
        sum_soft += int(result_soft[i])

    if sum_soft == 0:
        job1 = text['job_1']
    elif sum_soft >= 1:
        job1 = '✅ ' + text['job_1']

    if result[1] == '0':
        job2 = text['job_2']
    elif result[1] == '1':
        job2 = '✅ ' + text['job_2']

    if result[2] == '0':
        job3 = text['job_3']
    elif result[2] == '1':
        job3 = '✅ ' + text['job_3']
    if result[3] == '0':
        job4 = text['job_4']
    elif result[3] == '1':
        job4 = '✅ ' + text['job_4']
    if result[4] == '0':
        job5 = text['job_5']
    elif result[4] == '1':
        job5 = '✅ ' + text['job_5']

    if result[5] == '0':
        job6 = text['job_6']
    elif result[5] == '1':
        job6 = '✅ ' + text['job_6']

    if result[6] == '0':
        job7 = text['job_7']
    elif result[6] == '1':
        job7 = '✅ ' + text['job_7']

    if result[7] == '0':
        job8 = text['job_8']
    elif result[7] == '1':
        job8 = '✅ ' + text['job_8']


    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(job1)
    btn2 = types.KeyboardButton(job2)
    btn3 = types.KeyboardButton(job3)
    btn4 = types.KeyboardButton(job4)
    btn5 = types.KeyboardButton(job5)
    btn6 = types.KeyboardButton(job6)
    btn7 = types.KeyboardButton(job7)
    btn8 = types.KeyboardButton(job8)

    btn13 = types.KeyboardButton('Готово')
    markup.add(btn1).add(btn2).add(btn3).add(btn4).add(btn5).add(btn6).add(btn7).add(btn8).add(btn13)
    return markup

def choose_soft(message):
    data = backend.get_sphere1(message.from_user.username)
    result = list(data)
    #print(result)
    if result[0] == '0':
        soft1 = text['soft_1']
    elif result[0] == '1':
        soft1 = '✅ ' + text['soft_1']

    if result[1] == '0':
        soft2 = text['soft_2']
    elif result[1] == '1':
        soft2 = '✅ ' + text['soft_2']

    if result[2] == '0':
        soft3 = text['soft_3']
    elif result[2] == '1':
        soft3 = '✅ ' + text['soft_3']

    if result[3] == '0':
        soft4 = text['soft_4']
    elif result[3] == '1':
        soft4 = '✅ ' + text['soft_4']

    if result[4] == '0':
        soft5 = text['soft_5']
    elif result[4] == '1':
        soft5 = '✅ ' + text['soft_5']

    if result[5] == '0':
        soft6 = text['soft_6']
    elif result[5] == '1':
        soft6 = '✅ ' + text['soft_6']

    if result[6] == '0':
        soft7 = text['soft_7']
    elif result[6] == '1':
        soft7 = '✅ ' + text['soft_7']

    if result[7] == '0':
        soft8 = text['soft_8']
    elif result[7] == '1':
        soft8 = '✅ ' + text['soft_8']


    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(soft1)
    btn2 = types.KeyboardButton(soft2)
    btn3 = types.KeyboardButton(soft3)
    btn4 = types.KeyboardButton(soft4)
    btn5 = types.KeyboardButton(soft5)
    btn6 = types.KeyboardButton(soft6)
    btn7 = types.KeyboardButton(soft7)
    btn8 = types.KeyboardButton(soft8)
    btn13 = types.KeyboardButton('Назад')
    markup.add(btn1).add(btn2).add(btn3).add(btn4).add(btn5).add(btn6).add(btn7).add(btn8).add(btn13)
    return markup

def otkliki_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Назад')
    markup.add(btn1)
    return markup


def format():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Office')
    btn2 = types.KeyboardButton('Remote')
    btn3 = types.KeyboardButton('Hybrid')
    markup.add(btn1).add(btn2).add(btn3)
    return markup

def level():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('No experience')
    btn2 = types.KeyboardButton('Junior')
    btn3 = types.KeyboardButton('Middle')
    btn4 = types.KeyboardButton('Senior')
    btn5 = types.KeyboardButton('Teamlead')
    markup.add(btn1).add(btn2).add(btn3).add(btn4).add(btn5)
    return markup

def look_through():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Посмотреть!')
    markup.add(btn1)
    return markup

def vac():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Откликнуться')
    btn2 = types.KeyboardButton('Назад')
    btn3 = types.KeyboardButton('Меню')
    btn4 = types.KeyboardButton('Вперед')
    markup.add(btn1).add(btn2, btn3, btn4)
    return markup


def cancel():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Назад в меню')
    markup.add(btn1)
    return markup


@bot.message_handler(content_types=['audio', 'sticker', 'video', 'voice', 'location', 'contact'])
def echo(message):
    pass




bot.infinity_polling()
