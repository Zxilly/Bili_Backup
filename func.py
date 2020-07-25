import os
import json

def directory_check(path: str):
    if (not os.path.exists(path)):
        os.makedirs(path)

def path_generator(favname: str, bid= '', cid= ''):
    path = os.getcwd() + '/data/media/' + favname + '/'
    if (bid != ''):
        path += bid + '/'
        directory_check(path=path)
        # print(1)
    if (cid != ''):
        path += str(cid) + '/'
        directory_check(path=path)
    return path


def info_written(path,info,filename='info'):
    with open(path+filename+'.json','w+',encoding='UTF-8') as f:
        f.write(json.dumps(info,ensure_ascii=False))
        #print(f.read())

def download_media():
