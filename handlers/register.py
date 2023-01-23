from config import labeler, state_dispenser
from handlers.states import RegisterState
from models import User, Faculty, Group
from handlers.rules import NotRegisterUserRule
from vkbottle import Keyboard, KeyboardButtonColor, Text
from vkbottle.bot import Message


# заполнение номера группы пользователя
@labeler.message(state=RegisterState.GROUP)
async def set_group(message: Message):
    try:
        user = User.get(User.user_id == message.from_id)  # проверяем существование группы
        grp = Group.get(Group.course == user.course, Group.faculty == user.faculty, Group.number == int(message.text))
        user.group = grp  # если такая есть то записываем юзеру
        user.save()
        kb = Keyboard()  # херачим клаву и сообщение
        kb.add(Text("Профиль"), color=KeyboardButtonColor.PRIMARY)
        await state_dispenser.delete(message.peer_id)  # Убираем наконец-то диспенсер
        await message.answer("Отлично!\nРегистрация прошла успешно!\nТеперь, напиши \"Профиль\", чтобы "
                             "взаимодействовать с ботом.", keyboard=kb)
    except Group.DoesNotExist:
        pass


# заполнение номера курса пользователя
@labeler.message(state=RegisterState.COURSE_NUM)
async def set_course_num(message: Message):
    num = message.text.split()[0]  # получаем номер курса
    event = await state_dispenser.get(message.peer_id)  # берем из payload ступень образования
    char = event.payload["ctype"]
    groups = Group.select().where(Group.course == char + num).execute()  # берем список групп с ступенью + курс
    if groups:  # Если такие есть то делаем
        groups_dict = dict()  # Это для экономии места при выводе списка факультетов
        user = User.get(User.user_id == message.from_id)  # задаем пользователю его курс
        user.course = char + num
        user.save()
        kb = Keyboard()  # заполняем клавиатуру номерами курсов
        for i, grp in enumerate(groups):
            if i and not i % 5:
                kb.row()
            kb.add(Text(str(grp.number)), color=KeyboardButtonColor.SECONDARY)
            if groups_dict.get(grp.name) is None:  # сохраняем номера групп с одинаковыми названиями
                groups_dict[grp.name] = list()
            groups_dict[grp.name].append(str(grp.number))
        text = "Последний шажок! Мы уже на финише!\nВыберите свою группу:\n"  # Создаем текст с списками групп
        for gr, numbers in groups_dict.items():
            text += f"{', '.join(numbers)} - {gr}\n"  # номера групп - название направления
        await state_dispenser.set(message.peer_id, RegisterState.GROUP)  # меняем стейт
        await message.answer(text, keyboard=kb)


# заполнение курса пользователя
@labeler.message(state=RegisterState.COURSE_TYPE)
async def set_course_type(message: Message):
    user = User.get(User.user_id == message.from_id)
    ctypes = {"Бакалавриат": "b", "Магистратура": "m", "Специалитет": "s", "Аспирантура": "a", "Докторантура": "d"}
    if ctypes.get(message.text) in user.faculty.courses:
        num = int(user.faculty.courses[user.faculty.courses.index(ctypes.get(message.text)) + 1])  # кол-во курсов
        kb = Keyboard()
        for i in range(num):  # выводим все курсы клавиатурой
            if i:
                kb.row()
            kb.add(Text(f"{i + 1} курс"), color=KeyboardButtonColor.PRIMARY)
        await state_dispenser.set(message.peer_id, RegisterState.COURSE_NUM, ctype=ctypes[message.text])
        await message.answer("Выберите номер курса:", keyboard=kb)


# заполнение факультета пользователя
@labeler.message(state=RegisterState.FACULTY)
async def set_faculty(message: Message):
    try:
        await state_dispenser.set(message.peer_id, RegisterState.COURSE_TYPE)  # смена диспенсера
        fac = Faculty.get(Faculty.abbr == message.text)  # получаем строку факультета
        user = User.get(User.user_id == message.from_id)  # устанавливаем пользователю факультет
        user.faculty = fac
        user.save()
        kb = Keyboard()  # генерируем клавиатуру
        ctypes = {"b": "Бакалавриат", "m": "Магистратура", "s": "Специалитет", "a": "Аспирантура", "d": "Докторантура"}
        flag = True
        for char, txt in ctypes.items():  # в зависимости от строки в курсах, пишем типы курсов
            if char in fac.courses:
                if flag:  # в первый раз не добавляется ряд
                    flag = False
                else:
                    kb.row()
                kb.add(Text(txt), color=KeyboardButtonColor.POSITIVE)
        await message.answer("Супер! Теперь выберите вашу ступень образования:", keyboard=kb)
    except Faculty.DoesNotExist:
        return


# заполнение типа пользователя
@labeler.message(state=RegisterState.USER_TYPE, text=('Студент', 'Сторонний пользователь'))
async def set_user_type(message: Message):
    user = User.get(User.user_id == message.from_id)  # получаем пользователя
    if message.text == 'Сторонний пользователь':  # Если пользователь сторонний, то заканчиваем регистрацию
        user.role = 0
        user.save()
        kb = Keyboard()
        kb.add(Text('Профиль'), color=KeyboardButtonColor.PRIMARY)
        await state_dispenser.delete(message.peer_id)  # удаляем стейт
        await message.answer('Отлично! Спасибо за регистрацию!\nТеперь вы можете перейти в свой профиль:\n',
                             keyboard=kb)
    else:  # Если студент, то продолжаем регистрацию
        await state_dispenser.set(message.peer_id, RegisterState.FACULTY)  # Новый стейт
        kb = Keyboard()
        for i, f in enumerate(Faculty.select()):  # Делаем кнопки всех факультетов
            if i and i % 5:
                kb.row()
            kb.add(Text(f.abbr))
        await message.answer('Теперь выберите ваш факультет', keyboard=kb)


# Заполнение типа интерфейса
@labeler.message(state=RegisterState.INTERFACE, text=('Официальный клиент ВК', 'Старый или сторонний клиент ВК'))
async def set_interface_type(message: Message):
    user = User.get(User.user_id == message.from_id)  # получаем пользователя
    if message.text == 'Официальный клиент ВК':  # устанавливаем тип клиента в зависимости от ответа
        user.low_interface = False
    else:
        user.low_interface = True
    user.save()  # сохраняем
    kb = Keyboard()  # делаем новую клаву
    kb.add(Text('Студент'), color=KeyboardButtonColor.POSITIVE)
    kb.row()
    kb.add(Text('Сторонний пользователь'), color=KeyboardButtonColor.NEGATIVE)
    await state_dispenser.set(message.peer_id, RegisterState.USER_TYPE)  # меняем стейт
    await message.answer('А теперь укажите тип вашего аккаунта', keyboard=kb)


# Запуск регистрации
@labeler.message(NotRegisterUserRule(), text=('Start', 'Начать'))
async def start(message: Message):
    await state_dispenser.set(message.peer_id, RegisterState.INTERFACE)  # установка стейта
    kb = Keyboard()  # создание клавиатуры
    kb.add(Text('Официальный клиент ВК'), color=KeyboardButtonColor.PRIMARY)  # первая кнопка
    kb.row()  # новый ряд
    kb.add(Text('Старый или сторонний клиент ВК'), color=KeyboardButtonColor.NEGATIVE)  # вторая кнопка
    User.create(user_id=message.from_id)  # создаем пользователя в бд
    await message.answer('Привет! Для начала давай сделаем небольшую регистрацию:\n'
                         'Скажи, ты используешь обычный клиент ВК одной из последний версий, или ты '
                         'используешь сторонний клиент ВК или старую версию приложения?',
                         keyboard=kb)
