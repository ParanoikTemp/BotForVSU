from vkbottle.dispatch.dispenser import BaseStateGroup


class RegisterState(BaseStateGroup):
    INTERFACE = "type interface"  # окно с интерфейсом
    USER_TYPE = "type user"  # окно с выбором типа пользователя
    FACULTY = "faculty "  # окно с выбором факультета
    COURSE_TYPE = "course type"  # окно с выбором типа курса (бакалавр, магистр и т.д.)
    COURSE_NUM = "course number"  # окно с выбором номера курса
    GROUP = "group"  # окно с выбором группы


class SearchTeacherState(BaseStateGroup):
    TEACHER_LAST_NAME = 'teacher last name'
