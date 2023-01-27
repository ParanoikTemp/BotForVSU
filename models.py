from peewee import *

db = SqliteDatabase('databases/database.db')  # подключение базы данных


class Faculty(Model):
    name = TextField()
    abbr = TextField()
    courses = TextField()  # состоит из буквы и числа. Число - колво курсов. Буква: b - бакалавриат.
    # m - магистратура. s - специалитет. a - аспирантура. d - докторантура.
    data = TextField(default="{}")

    class Meta:
        database = db


class Group(Model):
    faculty = ForeignKeyField(Faculty)
    number = IntegerField()
    name = TextField()
    abbr = TextField()
    people = IntegerField(default=0)
    course = TextField()

    class Meta:
        database = db


class User(Model):  # Создание модели таблицы
    user_id = IntegerField(null=False, primary_key=True)  # id пользователя вк
    low_interface = BooleanField(default=False)  # интерфес (Если человек использует кастомный клиент или старый вк)
    faculty = ForeignKeyField(Faculty, null=True)
    course = TextField(default='')  # курс
    group = ForeignKeyField(Group, null=True)
    role = IntegerField(default=1)  # роль в бота
    data = TextField(default="{}")  # Дополнительная информация в json формате

    class Meta:
        database = db


class Teacher(Model):
    name1 = TextField()
    name2 = TextField()
    name3 = TextField()
    link = TextField()
    desc = TextField()
    photo = TextField(null=True)
    rating = DoubleField(default=0)
    voted = TextField(default="{}")

    class Meta:
        database = db


if __name__ == '__main__':
    db.create_tables([Teacher])
