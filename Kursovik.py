import configparser
import json
from pprint import pprint
from tqdm import tqdm
import requests


def read_token_vk():
    config = configparser.ConfigParser()
    config.read("settings.ini")
    access_token_vk = config['VK']['servis_key']
    return access_token_vk

def read_token_yd():
    config = configparser.ConfigParser()
    config.read("settings.ini")
    token_yd = config['YD']['access_token_yd']
    return token_yd

def result_to_json(list_info_files):
    with open('data.json', 'w') as json_file:
        json.dump(list_info_files, json_file)
    return json_file


class VK:

    def __init__(self, user_ids, version='5.199'):
        self.user_ids = user_ids
        access_token_vk = read_token_vk()
        self.base_address = 'https://api.vk.com/method/'
        self.params = { 'access_token': access_token_vk, 'v' : version }
        self.user_id = self.get_user_id(user_ids)

    def get_user_id(self, user_ids):
        self.user_ids = user_ids
        url = f'{self.base_address}users.get'
        params = {'user_ids': user_ids}
        params.update(self.params)
        responce = requests.get(url, params).json()
        user_id = responce['response'][0]['id']
        return user_id

    def get_photos(self, album_id='wall', extended=1, count=5, ):
        self.album_id = album_id
        url = f'{self.base_address}photos.get'
        params = {'owner_id': self.user_id, 'album_id': self.album_id, 'extended': extended}
        params.update(self.params)
        response = requests.get( url, params=params).json()
        return response

    def found_max_size_photo(self, count=5):
        list_sizes = ['w', 'z', 'y', 'r', 'q', 'p', 'o', 'x', 'm', 's']
        saved_photo = []
        count_saved_photo = 0
        photos_json = self.get_photos()
        for vol_size in list_sizes:
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


class YD:

    def __init__(self):
        token_yd = read_token_yd()
        self.headers = {'Authorization': token_yd}

    def create_folder_yadisk(self, folder_name):
        self.folder_name = folder_name
        yadi_url_put = 'https://cloud-api.yandex.net/v1/disk/resources'
        params = { 'path': folder_name }
        response = requests.put(yadi_url_put, headers=self.headers, params=params)
        return folder_name

    def save_file_yadisk(self, user_id, folder_name, count=5):
        self.user_id = user_id
        self.folder_name = folder_name
        list_info_files = []
        yadi_url_post = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        saved_photo = VK.found_max_size_photo(vk_client)
        folder = self.create_folder_yadisk(folder_name)
        for photo in tqdm(saved_photo, ncols=80):
            folder_url = f'{folder}/{photo['file_name']}'
            file_url = photo['file_url']
            params = {'path': folder_url,
                  'url': file_url}
            response = requests.post(yadi_url_post, headers=self.headers, params=params)
            res = {
                'file_name' : photo['file_name'],
                'size' : photo['size']
            }
            list_info_files.append(res)
        pprint(f'Файлы {list_info_files} были успешно сохранены на Яндекс Диске')
        return list_info_files



input_user_id = input('Введите id или screen_name пользователя Вконтакте: ')
input_folder_name = input('Введите название папки для Яндекс диска: ')


vk_client = VK(input_user_id)
yd_client = YD()
result = yd_client.save_file_yadisk(input_user_id, input_folder_name)
result_to_json(result)