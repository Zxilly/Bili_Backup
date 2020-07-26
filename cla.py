import math
import time
from datetime import datetime

import qrcode
import requests
import hashlib

from func import *
import hashlib
import math
import time
from datetime import datetime

import qrcode
import requests

from func import *
from aria2 import *


class User(object):
    def __init__(self):
        self.main_session = requests.session()
        self.check_cred()
        self.get_user_info()
        self.overall_info = {}
        self.failure_name = []
        aria2.set_global_options({
            'referer': 'https://www.bilibili.com/',
            'max-connection-per-server': 16,
        })

    def check_cred(self):
        try:
            with open('data/cred/cred.json', 'r+') as f:
                read_object = json.loads(f.read())
            if (datetime.now().timestamp() - read_object['generated_time'] > 15550000):
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
        if (os.name == 'posix'):
            qr_img.save('tmp/login.png', format='PNG')
            print('请扫描tmp/login.png')
        else:
            qr_img.show()
        self.login_polling(oauthKey)

    def login_polling(self, oauthKey: str):
        url = 'https://passport.bilibili.com/qrcode/getLoginInfo'
        post_form = {
            'oauthKey': oauthKey,
        }
        req = json.loads(self.main_session.post(url=url, data=post_form).content.decode())
        # print(req)
        if (req['status'] == False):
            time.sleep(2)
            self.login_polling(oauthKey=oauthKey)
        else:
            self.update_cred()

    def update_cred(self):
        cred = self.main_session.cookies.get_dict()
        written_object = {
            'generated_time': datetime.now().timestamp(),
            'cred': cred
        }
        with open('data/cred/cred.json', 'w+') as f:
            f.write(json.dumps(written_object))

    def update_session(self):
        with open('data/cred/cred.json', 'r+') as f:
            self.main_session.cookies.update(json.loads(f.read())['cred'])

    def get_user_info(self):
        url = 'https://api.bilibili.com/x/member/web/account'
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
        # print(json.dumps(fav_folder_list,ensure_ascii=False))
        # exit(0)
        self.get_fav_info(fav_folder_list)

    def get_media_info(self, page_max, id):
        url = 'https://api.bilibili.com/x/v3/fav/resource/list'
        overall_media = {}  # 整个文件夹中所有的视频
        for page_num in range(1, page_max + 1):
            get_param = {
                'media_id': id,
                'pn': page_num,
                'ps': 20
            }
            req = self.main_session.get(url=url, params=get_param)
            media_infos = json.loads(req.content.decode())['data']['medias']
            for media in media_infos:  # 单个视频
                bid = media['bvid']
                overall_media[bid] = {
                    'data': media,
                    'p': self.get_p_info(bid)
                }
        return overall_media

    def get_p_info(self, bid):
        url = 'https://api.bilibili.com/x/player/pagelist'
        p_info = {}
        req = self.main_session.get(url=url, params={'bvid': bid})
        data = json.loads(req.content.decode())['data']
        # print(data)
        for one_p in data:
            cid = one_p['cid']
            p_info[cid] = one_p
        return p_info

    def get_fav_info(self, fav_folder_list):
        for one_fav_folder in fav_folder_list:
            id = one_fav_folder['id']
            media_num = one_fav_folder['media_count']
            fav_folder_name = one_fav_folder['title']
            page_max = math.ceil(media_num / 20)
            # print(fav_folder_name)
            self.overall_info[fav_folder_name] = self.get_media_info(page_max, id)
        self.fav_differ()

    def fav_differ(self):
        self.differ_dict = {}
        try:
            with open('data/hist/info.json') as f:
                self.hist_differ_dict = json.loads(f.read())
        except:
            self.hist_differ_dict = {}
        # print(self.overall_info)
        for fav in self.overall_info:
            for media_key in self.overall_info[fav]:  # media_key == bvid
                for p_key in self.overall_info[fav][media_key]['p']:  # p_key == cid
                    hash = hashlib.md5((media_key + str(p_key)).encode()).hexdigest()
                    p_info = {
                        'bvid': media_key,
                        'cid': p_key
                    }
                    self.differ_dict[hash] = p_info
        self.added_fav_hash = list(set(self.differ_dict.keys()).difference(set(self.hist_differ_dict.keys())))
        self.removed_fav_hash = list(set(self.hist_differ_dict.keys()).difference(set(self.differ_dict.keys())))
        for one in self.added_fav_hash:
            bvid = self.differ_dict[one]['bvid']
            cid = self.differ_dict[one]['cid']
            print('bid:{},cid:{} started'.format(bvid,cid))
            self.media_download(bid=bvid,cid=cid)
        with open('tmp_json/failure.json','w+') as f:
            f.write(json.dumps(self.failure_name,ensure_ascii=False))
        with open('data/hist/info.json','w+') as f:
            f.write(json.dumps(self.differ_dict))

    def media_download(self,bid,cid):
        url = 'https://api.bilibili.com/x/player/playurl'
        get_params = {
            'bvid': bid,
            'cid': cid,
            'qn': 120,
            'fourk': 1
        }
        req = self.main_session.get(url=url, params=get_params)
        # print(req.content.decode()) #TODO:获取最高视频质量
        data = json.loads(req.content.decode())
        durl_list = data['data']['durl']
        if (len(durl_list) == 1):
            self.single_dl(durl_list,path_generator(bid=bid,cid=cid))
        else:
            self.multi_dl(durl_list,path_generator(bid=bid,cid=cid))
            #if(bid not in self.multipart_BV):
            #    self.multipart_BV.append(bid)

    def single_dl(self, url_list,path):
        url = url_list[0]['url']
        # print('start')
        # aria2.add_uris([url], options={'dir': path})
        self.dl([url],path)

    def multi_dl(self, url_list, path):
        urls = []
        for url in url_list:
            urls.append(url['url'])
        self.dl(urls,path)


    def dl(self,urls,path):
        dl_list = []
        while (True):
            if (len(aria2.get_downloads()) <= 13):
                aria2.add_uris(urls, options={'dir': path})
                break
            else:
                for one_dl in aria2.get_downloads():
                    if(one_dl.is_complete):
                        aria2.remove([one_dl])
                    elif(one_dl.has_failed):
                        if(aria2.resume([one_dl])):
                           time.sleep(1)
                           if(one_dl.has_failed):
                                self.failure_name.append(one_dl.name)
                                aria2.remove([one_dl])
                time.sleep(5)



"""
    def media_download(self,url):
        header = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36 Edg/84.0.522.40',
            'Referer':'https://www.bilibili.com'
        }
        req = self.page_session.get(url=url,stream=True,headers=header)
        with open(func.path_generator(favname=self.fav,bid=self.bid,cid=self.cid)+'media','wb') as f:
            a = 1
            for chunk in req.iter_content(chunk_size=1024*1024*4):
                if(chunk):
                    f.write(chunk)
                    print('chunk {} get'.format(a))
                    a+=1
"""
