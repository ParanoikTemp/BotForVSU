from vkbottle import API, BuiltinStateDispenser
from vkbottle.bot import BotLabeler
from tokens import token1
api = API(token=token1)
labeler = BotLabeler()
labeler.vbml_ignore_case = True
state_dispenser = BuiltinStateDispenser()