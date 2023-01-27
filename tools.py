from bs4 import BeautifulSoup
import requests
from PIL import Image
from config import uploader


async def upload_photo(link):
    try:
        s = BeautifulSoup(requests.get(link).content, 'lxml')
        photo_link = 'https://www.vsu.ru/ru/persons/' + s.find('img', {'class': 'pphotoright'})['src']
        photo_content = requests.get(photo_link).content
        with open('photo.jpg', 'wb') as f:
            f.write(photo_content)
        image = Image.open('photo.jpg').convert("RGBA")
        x, y = image.size
        y1 = y // 8 * 8
        x1 = y1 // 8 * 13
        image2 = Image.new(mode="RGB", size=(x1, y1), color=(255, 255, 255))
        image.thumbnail((round(x1 * (y1 / y)), y1))
        image2.paste(image, ((x1 - x) // 2, 0), image)
        image2.save('photo.jpg')
        result = await uploader.upload(album_id=291070338, paths_like='photo.jpg', group_id=218032620)
        return result[0][5:]
    except Exception as err:
        print('Ошибка при загрузке изображения:', err)
        return '-218032620_457239060'
