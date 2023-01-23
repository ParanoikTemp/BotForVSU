from vkbottle.dispatch.rules import ABCRule
from vkbottle.bot import Message
from models import User


class NotRegisterUserRule(ABCRule[Message]):  # класс правила для проверки регистрации пользователя (для первого раза)
    async def check(self, event: Message) -> bool:
        try:
            User.get(User.user_id == event.from_id)  # если пользователь найден, то рулз не срабатывает
            return False
        except User.DoesNotExist:  # Срабатывает если в коде сверху не нашелся запрос
            return True  # в противном случае он дает знать что пользователь новый


class InterfaceRule(ABCRule[Message]):  # класс правила которое устанавливает интерфейс для команды
    def __init__(self, low=False):
        self.low = low  # по умолчанию будет стоять обычный интерфейс

    async def check(self, event: Message) -> bool:
        try:
            return User.get(User.user_id == event.from_id).low_interface == self.low
            # совпадает ли тип интерфейса с требуемым
        except User.DoesNotExist:  # если пользователь не найден
            return False
