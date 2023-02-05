from peewee import *

db = SqliteDatabase('databases/database.db')  # подключение базы данных


class Faculty(Model):
    id = PrimaryKeyField(null=False, unique=True)
    name = TextField()
    abbr = TextField()
    data = TextField(default="{}")
    courses = TextField()  # состоит из буквы и числа. Число - кол-во курсов. Буква: b - бакалавриат.
                                      # m - магистратура. s - специалитет. a - аспирантура. d - докторантура. (Например: 3b, 1m)
    class Meta:
        database = db


class Group(Model):
    id = PrimaryKeyField(null=False, unique=True)
    faculty = ForeignKeyField(Faculty)
    number = IntegerField()
    name = TextField()
    abbr = TextField()
    course = TextField()

    class Meta:
        database = db


class User(Model):  # Создание модели таблицы
    id = IntegerField(null=False, primary_key=True)  # id пользователя вк
    low_interface = BooleanField(default=False)  # интерфес (Если человек использует кастомный клиент или старый вк)
    faculty = ForeignKeyField(Faculty, null=True)
    course = TextField(default='')  # курс
    group = ForeignKeyField(Group, null=True)
    role = IntegerField(default=1)  # роль в бота
    data = TextField(default="{}")  # Дополнительная информация в json формате

    class Meta:
        database = db


class Teacher(Model):
    id = PrimaryKeyField(null=False, unique=True)
    name1 = TextField()
    name2 = TextField(null=False)
    name3 = TextField()
    link = TextField()
    desc = TextField()
    photo = TextField(null=True)
    rating = DoubleField(default=0)
    voted = TextField(default="{}")

    class Meta:
        database = db


class LessonTime:
    number = IntegerField(default=1, primary_key=True, unique=True)
    start = TimeField(null=False)
    end = TimeField(null=False)

    class Meta:
        database = db


class Lesson:
    id = PrimaryKeyField(null=False, unique=True)
    short_name = TextField(null=False)
    full_name = TextField()

    class Meta:
        database = db


class ScheduleEntry:
    group = ForeignKeyField(Group, index=True, null=False)
    teacher = ForeignKeyField(Teacher, index=True, null=False)
    time = ForeignKeyField(LessonTime, index=True, null=False)
    lesson = ForeignKeyField(Lesson, index=True, null=False)
    week_day = TextField(index=True, null=False)
    type_of_week = TextField(index=True, null=False)
    sub_group = TextField(index=True, null=False)

    class Meta:
        database = db


if __name__ == '__main__':
    db.create_tables([Teacher])
