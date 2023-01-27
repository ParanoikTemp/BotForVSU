from vkbottle import API, BuiltinStateDispenser, PhotoToAlbumUploader
from vkbottle.bot import BotLabeler
from tokens import token1, upload_token
api = API(token=token1)  # апи бота
upload_api = API(token=upload_token)  # апи пользователя
uploader = PhotoToAlbumUploader(upload_api)  # аплоадер фотографий в альбом
labeler = BotLabeler()  # обработчик
labeler.vbml_ignore_case = True  # игнорирование регистра
state_dispenser = BuiltinStateDispenser()  # диспенсер
