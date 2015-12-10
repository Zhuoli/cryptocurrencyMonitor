'''
Created on Nov 8, 2015

@author: zhuoli
'''
import os
import datetime
import Constant

LOG_PATH = Constant.DATA_ROOT + "/Coin.log"
def AssertEqual(a, b):
    if a != b:
        raise Exception('Not equal');

def Log(message):
    if not os.path.exists(Constant.DATA_ROOT):
        os.makedirs(Constant.DATA_ROOT)
    time = str(datetime.datetime.now())
    secondIndex = time.rfind(':')
    time = time[:secondIndex]
    with open(LOG_PATH, "a") as log:
        log.write(time + ' : "' + message + '"\n')