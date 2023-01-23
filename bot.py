from vkbottle import Bot
from models import User
from config import api, state_dispenser
from handlers import labeler

bot = Bot(api=api, labeler=labeler, state_dispenser=state_dispenser)

if __name__ == '__main__':
    print('Bot is online!')
    User.delete().where(User.user_id != '0').execute()
    bot.run_forever()  # запуск бота
