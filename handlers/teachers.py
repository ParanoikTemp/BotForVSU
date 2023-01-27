from vkbottle.bot import Message, BotLabeler, MessageEvent
from handlers.rules import RegisteredUserRule, InterfaceRule
from models import User, Teacher
from config import state_dispenser, api
from vkbottle import TemplateElement, template_gen, KeyboardButtonColor, Keyboard, Text, Callback, GroupEventType
from handlers.states import SearchTeacherState
import json
from tools import upload_photo

teacher_labeler = BotLabeler()
teacher_labeler.vbml_ignore_case = True
teacher_labeler.auto_rules = [RegisteredUserRule()]  # Этот рулз автоматически возвращает объект пользователя


def make_template(teachers):  # функция которая создает карусель
    tlist = list()  # список, который потом будет преобразован в карусель
    without_image = list()  # преподаватели у которых нет фотографии
    for t in teachers:  # Для каждого препода делаем элемент карусели
        ###
        kb = Keyboard()
        kb.add(Text(f"Рейтинг: {t.rating}&#11088;"), color=KeyboardButtonColor.POSITIVE)  # вывод его рейтинга
        payload = {"type": "rate_teacher_msg", "teacher_id": t.id}
        kb.add(Callback(label="Оценить", payload=json.dumps(payload)))  # кнопка для оценки препода
        ###
        kb = json.loads(str(kb))['buttons'][0]  # извлекаем массив с кнопками
        if not t.photo:  # Если фото не найдено
            teacher_photo = '-218032620_457239092'  # по умолчанию ставим такую фотку
            without_image.append(t)  # добавляем в список преподов без фото
        else:
            teacher_photo = t.photo  # если найдено, то ставим раннее загруженное фото
        tlist.append(TemplateElement(  # создаем элемент карусели
            title=' '.join([t.name1, t.name2, t.name3]),  # ФИО препода
            description=t.desc,  # его научная степень
            photo_id=teacher_photo,  # его изображение
            action={"type": "open_link", "link": f"{t.link}"},  # если тык на картинку откроется сайт вгу
            buttons=kb  # ну и клавиатура само собой
        ))
    return template_gen(*tlist), without_image


def make_list(teachers):  # функция которая создает карусель
    attachments = list()  # список с вложениями
    tlist = list()  # список, который потом будет преобразован в текст
    without_image = list()  # преподаватели у которых нет фотографии
    for t in teachers:
        tlist.append(f'• {t.name1} {t.name2} {t.name3} - {t.desc}\nРейтинг преподавателя: {t.rating}&#11088;\n'
                     f'Страница на сайте: {t.link}')
        if not t.photo:  # Если фото не найдено
            attachments.append('photo-218032620_457239092')  # по умолчанию ставим такую фотку
            without_image.append(t)  # добавляем в список преподов без фото
        else:
            attachments.append('photo' + t.photo)  # если найдено, то ставим раннее загруженное фото
    return tlist, attachments, without_image


# Команда для поиска преподавателя
@teacher_labeler.message(text='Преподаватель')
async def get_profile(message: Message, user: User):
    await state_dispenser.set(message.peer_id, SearchTeacherState.TEACHER_LAST_NAME)
    await message.answer('Напишите фамилию преподавателя или его ФИО большими буквами')


# Функция для поиска преподавателя с полным интерфейсом
@teacher_labeler.message(InterfaceRule(), state=SearchTeacherState.TEACHER_LAST_NAME)
async def get_teacher(message: Message, user: User):
    await state_dispenser.delete(message.peer_id)  # удаляем стейт
    if len(message.text) == 3 and message.text.isupper():  # Если пользователь ввел ФИО
        txt = message.text
        teachers = Teacher.select().where(Teacher.name1.startswith(txt[0]), Teacher.name2.startswith(txt[1]),
                                          Teacher.name3.startswith(txt[2]))
    else:  # Если только фамилию, то ищем всех учителей с фамилией
        teachers = Teacher.select().where(Teacher.name1 == message.text.capitalize())
    if teachers:  # если учителя найдены
        template, without_image = make_template(teachers)  # генерируем карусель
        mess = await message.answer('Вот преподаватели по запросу:\n'
                                    '(Нажмите на фото преподавателя, чтобы перейти на его страницу на сайте ВГУ)',
                                    template=template)  # генерируем карусель и отправляем
        ###
        kb = Keyboard(inline=True)
        kb.add(Text('Профиль'), color=KeyboardButtonColor.PRIMARY)
        kb.row()
        kb.add(Text('Преподаватель'), color=KeyboardButtonColor.SECONDARY)
        ###
        await message.answer('Выберите действие', keyboard=kb)
        if without_image:  # если найдены преподаватели без фотографий, то запускаем скрит догрузки изображений
            for t in without_image:  # для каждого преподавателя без фото
                t.photo = await upload_photo(t.link)  # качаем фотку
                t.save()  # сохраняем
            template, _ = make_template(teachers)  # генерируем новую карусель
            await api.messages.edit(mess.peer_id, message='Вот преподаватели по запросу:\n(Нажмите на фото '
                                                          'преподавателя, чтобы перейти на его страницу на сайте ВГУ)',
                                    message_id=mess.message_id, template=template)  # меняем старую
    else:  # если же не найдены
        ###
        kb = Keyboard()
        kb.add(Text("Профиль"), color=KeyboardButtonColor.PRIMARY)
        kb.row()
        kb.add(Text("Преподаватель"), color=KeyboardButtonColor.SECONDARY)
        ###
        await message.answer('Увы, я не знаю преподавателя с такой фамилией :(\n'
                             'Если такой человек присутствует в преподавательском составе, уведомите об этом '
                             'администрацию проекта.', keyboard=kb)


# Функция для поиска преподавателя с урезанным интерфейсом
@teacher_labeler.message(InterfaceRule(True), state=SearchTeacherState.TEACHER_LAST_NAME)
async def get_teacher(message: Message, user: User):
    await state_dispenser.delete(message.peer_id)  # удаляем стейт
    if len(message.text) == 3 and message.text.isupper():  # Если пользователь ввел ФИО
        txt = message.text
        teachers = Teacher.select().where(Teacher.name1.startswith(txt[0]), Teacher.name2.startswith(txt[1]),
                                          Teacher.name3.startswith(txt[2]))
    else:  # Если только фамилию, то ищем всех учителей с фамилией
        teachers = Teacher.select().where(Teacher.name1 == message.text.capitalize())
    if teachers:  # если учителя найдены
        text, attachments, without_image = make_list(teachers)  # генерируем текст и картинки
        ###
        kb = Keyboard()
        kb.add(Text('Профиль'), color=KeyboardButtonColor.PRIMARY)
        kb.row()
        kb.add(Text('Преподаватель'), color=KeyboardButtonColor.SECONDARY)
        ###
        mess = await message.answer('Вот преподаватели по запросу:\n' + '\n'.join(text),
                                    attachment=attachments, keyboard=kb)  # генерируем текст и отправляем
        if without_image:  # если найдены преподаватели без фотографий, то запускаем скрит догрузки изображений
            for t in without_image:  # для каждого преподавателя без фото
                t.photo = await upload_photo(t.link)  # качаем фотку
                t.save()  # сохраняем
            text, attachments, _ = make_list(teachers)  # генерируем текст и новые картинки
            await api.messages.edit(mess.peer_id, message='Вот преподаватели по запросу:\n' + '\n'.join(text),
                                    message_id=mess.message_id, attachment=attachments, keyboard=kb)  # меняем старую
    else:  # если же не найдены
        ###
        kb = Keyboard()
        kb.add(Text("Профиль"), color=KeyboardButtonColor.PRIMARY)
        kb.row()
        kb.add(Text("Преподаватель"), color=KeyboardButtonColor.SECONDARY)
        ###
        await message.answer('Увы, я не знаю преподавателя с такой фамилией :(\n'
                             'Если такой человек присутствует в преподавательском составе, уведомите об этом '
                             'администрацию проекта.', keyboard=kb)


@teacher_labeler.raw_event(GroupEventType.MESSAGE_EVENT, payload_contains={"type": "rate_teacher_msg"},
                           dataclass=MessageEvent)  # Если это нажатие на callback кнопку, с тегом оценки препода
async def get_rate_teacher(event: MessageEvent):
    tc = event.payload['teacher_id']
    teacher = Teacher.get(Teacher.id == tc)
    ###
    kb = Keyboard(inline=True)  # делаем клавиатуру с рейтингом от 1 до 5
    for i in range(1, 6):
        kb.add(Callback(f'{i}&#11088;', payload={"type": "rate_teacher_num", "rating": i, "teacher_id": tc}))
    ###
    await event.send_message('Поставьте оценку преподавателю:\t'  # отправляем сообщение
                             f'{teacher.name1} {teacher.name2} {teacher.name3}', keyboard=kb)


@teacher_labeler.raw_event(GroupEventType.MESSAGE_EVENT, payload_contains={"type": "rate_teacher_num"},
                           dataclass=MessageEvent)  # если человек выставил рейтинг преподавателю
async def get_rate_teacher(event: MessageEvent):
    tc = event.payload['teacher_id']  # получаем id препода
    num = event.payload['rating']  # получаем оценку (от 1 до 5)
    teacher = Teacher.get(Teacher.id == tc)  # получаем объект препода
    voted: list = json.loads(teacher.voted)  # получаем список проголосовавших
    for i, u in enumerate(voted):  # проверяем, голосовал ли человек раннее
        if u[0] == event.user_id:  # если голосовал
            voted[i] = [event.user_id, num]  # меняем раннее выставленную оценку
            teacher.voted = json.dumps(voted)
            await event.edit_message(  # изменяем предыдущую оценку
                f'Вы успешно изменили оценку преподавателю: {num}\n{teacher.name1} {teacher.name2}'
                f' {teacher.name3}')
            break
    else:  # если раннее не голосовал
        voted.append([event.user_id, num])  # добавляем голос человека
        teacher.voted = json.dumps(voted)
        await event.edit_message(f'Вы успешно поставили оценку преподавателю: {num}\n{teacher.name1} {teacher.name2}'
                                 f' {teacher.name3}')  # меняем сообщение
    teacher.rating = round(sum(list(map(lambda x: x[1], voted))) / len(voted), 1)  # сохраняем значен рейтинга препода
    teacher.save()  # сохраняем изменения
    await event.show_snackbar('Спасибо за оценку :)')  # выкидываем сверху окошко с благодарностью
