from config import labeler, state_dispenser
from handlers.states import RegisterState
from models import User, Faculty, Group
from handlers.rules import NotRegisterUserRule
from vkbottle import Keyboard, KeyboardButtonColor, Text
from vkbottle.bot import Message


# заполнение факультета пользователя
@labeler.message(state=RegisterState.FACULTY)
async def set_faculty(message: Message):
    try:
        fac = Faculty.get(Faculty.abbr == message.text)
        
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
        await message.answer('Отлично! Спасибо за регистрацию!\nТеперь вы можете перейти в свой профиль:\n', keyboard=kb)
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
