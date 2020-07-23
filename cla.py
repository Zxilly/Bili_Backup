import json
from datetime import datetime

import requests
from PIL import Image
import qrcode
import os

import data
import func

import io
import time
import math


class User(object):
    def __init__(self):
        self.main_session = requests.session()
        self.check_cred()
        self.get_user_info()

    def check_cred(self):
        try:
            with open('data/cred/cred.json','r+') as f:
                read_object = json.loads(f.read())
            if(datetime.now().timestamp()-read_object['generated_time']>15550000):
                raise Exception('cred expired')
            else:
                self.update_session()
        except:
            raise Exception('no cred')

    def login(self):
        url = 'https://passport.bilibili.com/qrcode/getLoginUrl'
        data = json.loads(self.main_session.get(url=url).content)
        # print(data)
        qr_data = data['data']['url']
        oauthKey = data['data']['oauthKey']
        qr_img = qrcode.make(qr_data)
        if(os.name=='posix'):
            qr_img.save('tmp/login.png',format='PNG')
            print('请扫描tmp/login.png')
        else:
            qr_img.show()
        self.login_polling(oauthKey)

    def login_polling(self,oauthKey:str):
        url ='http://passport.bilibili.com/qrcode/getLoginInfo'
        post_form = {
            'oauthKey':oauthKey,
        }
        req = json.loads(self.main_session.post(url=url,data=post_form).content.decode())
        print(req)
        if(req['status']==False):
            time.sleep(2)
            self.login_polling(oauthKey=oauthKey)
        else:
            self.update_cred()

    def update_cred(self):
        cred = self.main_session.cookies.get_dict()
        written_object = {
            'generated_time':datetime.now().timestamp(),
            'cred':cred
        }
        with open('data/cred/cred.json','w+') as f:
            f.write(json.dumps(written_object))

    def update_session(self):
        with open('data/cred/cred.json','r+') as f:
            self.main_session.cookies.update(json.loads(f.read())['cred'])

    def get_user_info(self):
        url = 'http://api.bilibili.com/x/member/web/account'
        data = json.loads(self.main_session.get(url=url).content.decode())
        # print(data)
        self.usrid = data['data']['mid']
        # print(self.usrid)

    def get_fav_folder_info(self):
        url = 'https://api.bilibili.com/x/v3/fav/folder/list4navigate'
        req = self.main_session.get(url=url)
        # print(req.content.decode())
        data = json.loads(req.content.decode())
        fav_folder_list = data['data'][0]['mediaListResponse']['list']
        self.get_fav_info(fav_folder_list)

    def get_fav_info(self,fav_folder_list):
        url = 'https://api.bilibili.com/x/v3/fav/resource/list?media_id=50550882&pn=1&ps=20'
        for one_fav_folder in fav_folder_list:
            id = one_fav_folder['id']
            media_num = one_fav_folder['media_count']
            fav_folder_name = one_fav_folder['title']
            func.directory_check(name=fav_folder_name)
            page_max = math.ceil(media_num/20)
            for page_num in range(1,page_max+1):
                get_param = {
                    'media_id': id,
                    'pn': page_num,
                    'ps': 20
                }
                req = self.main_session.get(url=url,params=get_param)
                media_infos = json.loads(req.content.decode())['data']['medias']
                for media in media_infos:
                    pass














