from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_kb():
    kb_list = [
        [KeyboardButton(text="📖 Организационная информация")],
        [KeyboardButton(text="📝 Рабочие процессы")],
        [KeyboardButton(text="📬 Обратная связь и поддержка")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True, one_time_keyboard=True, input_field_placeholder="Ваше сообщение")

    return keyboard

def info_kb_1():
    info_kb_list = [
        [KeyboardButton(text="Корпоративная политика и правила")], # вопрос 1
        [KeyboardButton(text="Инфраструктура компании")], # вопрос 2
        [KeyboardButton(text="Документация")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=info_kb_list, resize_keyboard=True, one_time_keyboard=True,
                                   input_field_placeholder="Ваше сообщение")
    return keyboard

def info_kb_2():
    info_kb_list1 = [
        [KeyboardButton(text="Взаимодействие с коллегами")],
        [KeyboardButton(text="Техническая поддержка")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=info_kb_list1, resize_keyboard=True,
                                   input_field_placeholder="Ваше сообщение")
    return keyboard

def info_kb_3():
    info_kb_list2 = [
        [KeyboardButton(text="Опросы удовлетворенности")],
        [KeyboardButton(text="Решение проблем")],
        [KeyboardButton(text="Мотивация")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=info_kb_list2, resize_keyboard=True,
                                   input_field_placeholder="Ваше сообщение")
    return keyboard

def info_kb_1_1():
    info_kb_list_1 = [
        [KeyboardButton(text="Больничный")],
        [KeyboardButton(text="Отпуск")],
        [KeyboardButton(text="Командировки")],
        [KeyboardButton(text="Льготы и компенсации для сотрудников")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=info_kb_list_1, resize_keyboard=True, one_time_keyboard=True,
                                   input_field_placeholder="Ваше сообщение")
    return keyboard

def info_kb_1_2():
    info_kb_list1_1 = [
        [KeyboardButton(text="Факультеты университета")],
        [KeyboardButton(text="Адреса корпусов")],
        [KeyboardButton(text="Парковка для сотрудников")],
        [KeyboardButton(text="Ближайшие столовые и кафе")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=info_kb_list1_1, resize_keyboard=True, one_time_keyboard=True,
                                   input_field_placeholder="Ваше сообщение")
    return keyboard

def info_kb_1_3():
    info_kb_list1_2 = [
        [KeyboardButton(text="Шаблоны документов")],
        [KeyboardButton(text="Должностные инструкции")],
        [KeyboardButton(text="Доступ к внутренним регламентам и политике университета")],
        [KeyboardButton(text="Шаблоны заявлений и отчетов")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=info_kb_list1_2, resize_keyboard=True, one_time_keyboard=True,
                                   input_field_placeholder="Ваше сообщение")
    return keyboard

def info_kb_2_1():
    info_kb_list2_1 = [
        [KeyboardButton(text="Контакты")],
        [KeyboardButton(text="Вопросы к HR")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=info_kb_list2_1, resize_keyboard=True, one_time_keyboard=True,
                                   input_field_placeholder="Ваше сообщение")
    return keyboard

def info_kb_2_2():
    info_kb_list2_2 = [
        [KeyboardButton(text="Помощь по техническим вопросам")],
        [KeyboardButton(text="Доступ к корпоративным ресурсам")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=info_kb_list2_2, resize_keyboard=True, one_time_keyboard=True,
                                   input_field_placeholder="Ваше сообщение")
    return keyboard

def info_kb_3_1():
    info_kb_list3_1 = [
        [KeyboardButton(text="Процесс оценки сотрудников")],
        [KeyboardButton(text="Анонимная обратная связь")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=info_kb_list3_1, resize_keyboard=True, one_time_keyboard=True,
                                   input_field_placeholder="Ваше сообщение")
    return keyboard

def info_kb_3_2():
    info_kb_list3_2 = [
        [KeyboardButton(text="Сложности на работе")],
        [KeyboardButton(text="Отзывы")],
        [KeyboardButton(text="Общение с HR")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=info_kb_list3_2, resize_keyboard=True, one_time_keyboard=True,
                                   input_field_placeholder="Ваше сообщение")
    return keyboard


def info_kb_3_3():
    info_kb_list3_3 = [
        [KeyboardButton(text="Курсы повешения квалификации")],
        [KeyboardButton(text="Текущие проекты")],
        [KeyboardButton(text="Вакансии внутри университета")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=info_kb_list3_3, resize_keyboard=True, one_time_keyboard=True,
                                   input_field_placeholder="Ваше сообщение")
    return keyboard

