import pandas as pd
import datetime
import re
from config import *
from pony.orm import *


db = Database()

class Vacancies(db.Entity):
    username = Required(str)
    vac_id = Optional(str)
    name = Optional(unicode)
    company = Optional(unicode)
    vacancy = Optional(unicode)
    dtime = Optional(str)

class Users(db.Entity):
    username = Required(str)
    chat_id = Optional(str)
    sphere = Optional(str)
    format = Optional(str)
    city = Optional(str)
    net = Optional(str)
    status = Optional(str)
    level = Optional(str)
    sphere1 = Optional(str)

class Not_found(db.Entity):
    username = Required(str)
    time = Optional(str)


db.bind(provider='mysql', host='127.0.0.1', user='root', passwd='0000', db='hr', charset='utf8mb4', use_unicode=True)
db.generate_mapping(create_tables=True)


def has_cyrillic(text):
    return bool(re.search('[а-яА-Я]', text))

def data_file(name = 'data.xlsx'):
    return pd.read_excel(name)

def data_info():
    file = data_file()
    level = file['Опыт']
    sphere = file['Сфера']
    format = file['Формат']
    return sphere, level, format

def base_info(f = 0):
    file = data_file()
    comp = file['Компания']
    pos = file['Должность']
    net = file['Вилка']
    loc = file['Место работы']
    who = file['Кто ищет']
    des = file['Описание: html']
    id = file['id']
    if f == 1:
        return pos, comp, id
    else:
        return comp, pos, net, loc, who, des

def fvac(i):
    p, c, id = base_info(1)
    return p[i], c[i], id[i]

def fbase(i):
    c, p, n, l, w, d = base_info()
    return c[i], p[i], n[i], l[i], w[i], d[i]


# Подробнее
def more():
    return list(data_file()['Подробнее'])
# Id
def id():
    return list(data_file()['id'])


def fmore(i):
    return more()[i]
def fid(i):
    return id()[i]


# Vacancy number
def vac_number(more):
    return len(more)

# Vacancy number with filters
def vac_for_me(username):
    row = []
    data = unpack_sphere(username)
    sphere, level, format = data_info()
    for j in range(len(data)):
        for i in range(len(more())):
            if level[i] == get_level(username) and data[j] == sphere[i] and format[i] == get_format(username):
                row.append(i)
    return row

def unpack_sphere(username):
    result = []
    data = get_sphere(username)
    datad = list(data)
    data1 = get_sphere1(username)
    datad1 = list(data1)
    for i in range(len(datad)):
        if datad[i] == '1':
            result.append(jobs[i])
    for i in range(len(datad1)):
        if datad1[i] == '1':
            result.append(softs[i])
    return result



""" DataBase """
@db_session
def create_user(username, chat_id):
    sphere = '0' * len(jobs)
    sphere1 = '0' * len(softs)
    query = select(p for p in Users if p.username == username)
    amount = len(query)
    if amount == 0:
        Users(username=username, chat_id=str(chat_id), sphere=sphere, status='0', sphere1=sphere1)
    else:
        pass


@db_session
def update_sphere(username, sphere):
    id = Users.get(username=username).id
    Users[id].sphere = sphere

@db_session
def update_sphere1(username, sphere):
    id = Users.get(username=username).id
    Users[id].sphere1 = sphere

@db_session
def get_sphere(username):
    user = Users.get(username=username)
    return user.sphere

@db_session
def get_sphere1(username):
    user = Users.get(username=username)
    return user.sphere1

@db_session
def update_salary(username, salary):
    id = Users.get(username=username).id
    Users[id].net = salary

@db_session
def update_city(username, city):
    id = Users.get(username=username).id
    Users[id].city = city

@db_session
def update_format(username, format):
    id = Users.get(username=username).id
    Users[id].format = format

@db_session
def update_status(username):
    id = Users.get(username=username).id
    Users[id].status = '1'

@db_session
def update_level(username, level):
    id = Users.get(username=username).id
    Users[id].level = level

@db_session
def get_status(username):
    user = Users.get(username=username)
    return user.status


@db_session
def get_level(username):
    user = Users.get(username=username)
    if user.level == "No experience":
        return "Без опыта"
    else:
        return user.level

@db_session
def get_format(username):
    user = Users.get(username=username)
    f = user.format
    if f == "Office":
        return "Офис"
    elif f == "Remote":
        return "Дистанционно"
    else:
        return "Гибрид"


@db_session
def update_vcs(username, i):
    vacancy = fmore(i)
    name, company, id = fvac(i)
    ls = get_vacancies(username, 1)
    dtime = datetime.datetime.now()
    try:
        if vacancy not in ls:
            Vacancies(username=username, vac_id=str(id), dtime=str(dtime))

        else:
            pass
    except:
        Vacancies(username=username, vac_id=str(id), dtime=str(dtime))



@db_session
def get_times(username):
    times = select(n for n in Vacancies if n.username==username)
    try:
        tms = []
        for row in times:
            tms.append(str(row.dtime).split(' ')[0])
        return tms
    except:
        return None


@db_session
def get_ids(username):
    all_ids = select(n for n in Vacancies if n.username==username)
    try:
        ids = []
        for row in all_ids:
            ids.append(str(row.vac_id))
        return ids
    except:
        return None


@db_session
def get_vacancies(username, flag):
    tms = get_times(username)
    ids = get_ids(username)
    vacancies = select(n for n in Vacancies if n.username==username)

    try:
        i = 0
        vcs = ""
        vcs1 = []
        for row in vacancies:
            vcs1.append(str(row.vacancy))
            #vcs += '*' + str(i + 1) + '*' + '.\n' + "*Дата отклика:* " + str(tms[i]) + '\n' + "*Компания:* " + str(cms[i]) + '\n' + "*Должность:* " +  str(nms[i]) + '\n' + "*Контакты:* " + str(row['vacancy']) + '\n\n'
            vcs += '*' + str(i + 1) + '*' + '.\n' + "*Дата отклика:* " + str(tms[i]) + '\n' + "*ID вакансии:* " + str(ids[i]) + '\n\n'
            i += 1
        if i == 0:
            return None
        if flag == 0:
            return vcs
        if flag == 1:
            return vcs1
    except:
        return None


@db_session
def not_f(username):
    time = datetime.datetime.now()
    Not_found(username=username, time=str(time))


""" Vacancy cards """
def card(vac):
    fc, fp, fn, fl, fw, fd = fbase(vac)
    fm = fmore(vac)
    return f'*Компания: *{fc}\n*Должность: *{fp}\n*Локация: *{fl}\n*Вилка: *{fn}\n\n*----------------  Кто ищет*\n{fw}\n\n*----------------  Описание*\n{fd}\n\n*Контакт:*\n{fm}'



