import configparser
import json
from pprint import pprint
from tqdm import tqdm
import requests

config = configparser.ConfigParser()
config.read("settings.ini")
VK_TOKEN = config['VK']['servis_key']
YD_TOKEN = config['YD']['access_token_yd']


class VK:

    list_sizes = ['w', 'z', 'y', 'r', 'q', 'p', 'o', 'x', 'm', 's']

    def __init__(self, access_token_vk, version='5.199'):

        self.base_address = 'https://api.vk.com/method/'
        self.params = { 'access_token': access_token_vk, 'v' : version }

    def get_photos(self, user_id, extended=1, count=5, album_id='wall'):

        url = f'{self.base_address}photos.get'
        params = {'owner_id': user_id, 'album_id': album_id, 'extended': extended}
        params.update(self.params)
        response = requests.get( url, params=params).json()
        return response


    def found_max_size_photo(self, user_id, count=5):

        self.user_id = user_id
        saved_photo = []
        count_saved_photo = 0
        photos_json = self.get_photos(user_id)
        for vol_size in self.list_sizes:
            for photo in photos_json['response']['items']:
                for photo_size in photo['sizes']:
                    if photo_size['type'] == vol_size:
                        photo_data = {'size': photo_size['type'],
                                               'file_name': photo['likes']['count'],
                                               'file_url': photo['orig_photo']['url']}
                        if count_saved_photo < count:
                            for i in saved_photo:
                                if i['file_name'] == photo_data['file_name']:
                                    photo_data['file_name'] = str(photo['likes']['count']) + '_' + str(photo['date'])
                            count_saved_photo += 1
                            saved_photo.append(photo_data)
        return saved_photo

    def create_folder_yadisk(self, folder_name):

        self.folder_name = folder_name
        yadi_url_put = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = { 'Authorization': YD_TOKEN }
        params = { 'path': folder_name }
        response = requests.put(yadi_url_put, headers=headers, params=params)
        return folder_name

    def save_file_yadisk(self, folder_name, user_id, count=5):
        result = []
        yadi_url_post = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = {'Authorization': YD_TOKEN}
        saved_photo = self.found_max_size_photo(user_id)
        folder = self.create_folder_yadisk(folder_name)
        for photo in tqdm(saved_photo, ncols=80):
            folder_url = f'{folder}/{photo['file_name']}'
            file_url = photo['file_url']
            params = {'path': folder_url,
                  'url': file_url}
            response = requests.post(yadi_url_post, headers=headers, params=params)
            res = {
                'file_name' : photo['file_name'],
                'size' : photo['size']
            }
            result.append(res)
        with open('data.json', 'w') as json_file:
            json.dump(result, json_file)
        return json_file, pprint(f'Файлы {result} были успешно сохранены на Яндекс Диске')


vk_client = VK(VK_TOKEN)
vk_client.save_file_yadisk('название папки', ID пользователя ВК)
