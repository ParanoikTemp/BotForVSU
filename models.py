from peewee import *

db = SqliteDatabase('databases/database.db')  # подключение базы данных


class User(Model):  # Создание модели таблицы
    user_id = IntegerField(null=False, primary_key=True)  # id пользователя вк
    low_interface = BooleanField(default=False)  # интерфес (Если человек использует кастомный клиент или старый вк)
    faculty = TextField(default='')  # название факультета
    course = TextField(default='')  # курс
    group = IntegerField(default=0)  # группа
    role = IntegerField(default=1)  # роль в бота
    data = TextField(default="{}")  # Дополнительная информация в json формате

    class Meta:
        database = db


class Faculty(Model):
    name = TextField()
    people = IntegerField(default=0)
    abbr = TextField()
    courses = TextField()  # состоит из буквы и числа. Число - колво курсов. Буква: b - бакалавриат.
    # m - магистратура. s - специалитет. a - аспирантура. d - докторантура.
    data = TextField(default="{}")

    class Meta:
        database = db


class Group(Model):
    faculty = IntegerField()
    number = IntegerField()
    name = TextField()
    abbr = TextField()
    people = IntegerField(default=0)
    course = TextField()

    class Meta:
        database = db


if __name__ == '__main__':
    db.create_tables([Faculty, Group])
