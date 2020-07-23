import hashlib
import data
import os

def directory_check(name:str):
    path = os.getcwd()+'/data/media/'+name+'/'
    if(not os.path.exists(path)):
        os.makedirs(os.getcwd()+'/data/media/'+name+'/')
        print(1)