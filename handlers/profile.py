from vkbottle.bot import Message, BotLabeler
from handlers.rules import RegisteredUserRule, RoleRule
from models import User
from config import api, state_dispenser
from vkbottle import Keyboard, KeyboardButtonColor, Text

profile_labeler = BotLabeler()
profile_labeler.vbml_ignore_case = True
profile_labeler.auto_rules = [RegisteredUserRule()]


@profile_labeler.message(RoleRule((1, )), text='Профиль')
async def get_profile(message: Message, user: User):
    await state_dispenser.delete(message.peer_id)  # Зачистка стейтов
    udata, = await api.users.get(message.from_id)  # получение информации о пользователе
    ctypes = {"b": "Бакалавриат", "m": "Магистратура", "s": "Специалитет", "a": "Аспирантура", "d": "Докторантура"}
    ###
    kb = Keyboard(one_time=True)
    kb.add(Text('Преподаватель'), color=KeyboardButtonColor.SECONDARY)
    ###
    await message.answer(f'<= Информация профиля =>\n'
                         f'&#128100;Имя: {udata.first_name} {udata.last_name}\n'
                         f'&#127963;Факультет: {user.faculty.name} ({user.faculty.abbr})\n'
                         f'&#127891;Ступень обучения: {ctypes[user.course[0]]} {user.course[1]} курс\n'
                         f'&#128107;Группа №{user.group.number} - {user.group.name} ({user.group.abbr})',
                         keyboard=kb)
