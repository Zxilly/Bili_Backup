class Media(object):
    def __init__(self, bid, fav, session):
        self.bid = bid
        self.fav = fav
        self.media_session = session
        self.get_p_info()

    def get_p_info(self):
        url = 'https://api.bilibili.com/x/player/pagelist'
        req = self.media_session.get(url=url,params={'bvid':self.bid})
        data = json.loads(req.content.decode())['data']
        for one_p in data:
            cid = one_p['cid']
            func.info_written(func.path_generator(favname=self.fav,bid=self.bid,cid=cid),info=one_p)
            one = Page(bid=self.bid,cid=cid,session=self.media_session,fav=self.fav)

class Page(object):
    def __init__(self, bid, cid, session, fav):
        self.bid = bid
        self.cid = cid
        self.page_session = session
        self.fav = fav
        self.get_play_url()


    def get_play_url(self):
        url = 'https://api.bilibili.com/x/player/playurl'
        get_params = {
            'bvid':self.bid,
            'cid':self.cid,
            'qn':120,
            'fourk':1
        }
        req = self.page_session.get(url=url,params=get_params)
        # print(req.content.decode()) #TODO:获取最高视频质量
        data = json.loads(req.content.decode())
        durl_list = data['data']['durl']
        if(len(durl_list)==1):
            self.single_dl(durl_list)

    def single_dl(self,url_list):
        url = url_list[0]['url']
        self.media_download(url=url)


    def media_download(self,url):
        header1 = "\"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36 Edg/84.0.522.40\""

        header2 = "\"Referer: https://www.bilibili.com\""
        com = 'aria2c '+'--header='+header1+' '+'--header='+header2+' '+'-x2'+' '+'--dir='+func.path_generator(favname=self.fav,bid=self.bid,cid=self.cid)+' '+'"'+url+'"'
        # print(com)
        with os.popen(com, "r") as p:
            r = p.readlines()
            print(r)
        exit(0)
