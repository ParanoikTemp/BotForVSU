from vkbottle.dispatch.rules import ABCRule
from vkbottle.bot import Message
from models import User
from typing import Union, Tuple, List


class NotRegisterUserRule(ABCRule[Message]):  # класс правила для проверки регистрации пользователя (для первого раза)
    async def check(self, event: Message) -> bool:
        try:
            User.get(User.user_id == event.from_id)  # если пользователь найден, то рулз не срабатывает
            return False
        except User.DoesNotExist:  # Срабатывает если в коде сверху не нашелся запрос
            return True  # в противном случае он дает знать что пользователь новый


class RegisteredUserRule(ABCRule[Message]):  # класс правила для проверки регистрации пользователя
    async def check(self, event: Message) -> bool:
        try:
            return {"user": User.get(User.user_id == event.from_id)}  # если пользователь найден, то рулз его вернет
        except User.DoesNotExist:  # Срабатывает если в коде сверху не нашелся запрос
            return False  # в противном случае он дает знать что пользователя нет


class InterfaceRule(ABCRule[Message]):  # класс правила которое устанавливает интерфейс для команды
    def __init__(self, low: bool = False):
        self.low = low  # по умолчанию будет стоять обычный интерфейс

    async def check(self, event: Message) -> bool:
        try:
            return User.get(User.user_id == event.from_id).low_interface == self.low
            # совпадает ли тип интерфейса с требуемым
        except User.DoesNotExist:  # если пользователь не найден
            return False


class RoleRule(ABCRule[Message]):  # класс правила который проверяет совпадение роли у человека
    def __init__(self, roles: Union[int, Tuple[int, ...], List[int]]):
        self.roles = roles  # ролями может быть как число, так и список (кортеж) чисел

    async def check(self, event: Message) -> bool:
        try:
            if type(self.roles) is int:  # если передано только одно число
                return User.get(User.user_id).role == self.roles  # сравниваем полностью
            else:  # иначе это список или кортеж
                return User.get(User.user_id).role in self.roles  # тогда проверяем вхождение
        except User.DoesNotExist:
            return False  # если пользователь не найден, то вовращаем false
