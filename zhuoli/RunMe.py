'''
Digit Currency Monitor - V1.0
Created on Nov 8, 2015

@author: zhuoli
'''
import json
import os
import sys
import time
import traceback

import httplib2

import ConsoleUtilities
import Constant
from DataKeeper import DataKeeper
from Email import Email
from Errors import Log
import Errors


DATA_PATH = Constant.DATA_ROOT + '/priceLog.csv'
BTC = ['BitCoin',"http://coinmarketcap-nexuist.rhcloud.com/api/btc/price"]
LTC = ['LiteCoin',"http://coinmarketcap-nexuist.rhcloud.com/api/ltc/price"]
DOGE = ['DOGECOIN', "http://coinmarketcap-nexuist.rhcloud.com/api/doge/price"]
RECIPIENT = 'zhuoliseattle@gmail.com'
COINS = [BTC, LTC, DOGE]
SLEEP_SECONDS = 10 * 60 # Refresh price interval
HOUR = 8 # Monitor interval
MONITOR_WINDOW = HOUR * 60 * 60 # 1 hours monitor history

# When should consider buy coins
SELL_ALERT_THRESHOLD = 0.05

# When should consider sell coins
BUY_ALERT_THRESHOLD = 0.05

# Alert for oscillation
OSCILLATION_ALERT_THRESHOLD = 0.1

def main():
    
    # Create data folder
    if not os.path.exists(Constant.DATA_ROOT):
        os.makedirs(Constant.DATA_ROOT)
        
    #TODO change hardcode password to console input
    pw = 'lzl8482617' #input("\nEnter password:\n");
    email = Email("robotonyszu@gmail.com", pw)
    try:
        email.Authenticate()
    except Exception as e:
        ConsoleUtilities.WriteLine("Email authenticate failed, quite application: " + e)
        Log("Email authenticate failed, quite application: " + str(e))
        sys.exit(-1)
        
    ConsoleUtilities.WriteLine("Email authenticate succeed")
    ConsoleUtilities.WriteLine("Monitor started...")
    email.send_email(RECIPIENT, 'Hi there, the CurrencyMonitor is launched', 'Send by CurrencyMonitor')
    while True:
        try:
            Monitor(email)
        except Exception:
            stacktrace = traceback.format_exc()
            Log("CoinMonitor Restarted due to exception" + stacktrace)
            ConsoleUtilities.WriteLine(stacktrace)
            email.send_email(RECIPIENT, "CoinMonitor Restarted due to exception", stacktrace)
        time.sleep(180);

def Monitor(email):
    num = int(MONITOR_WINDOW / SLEEP_SECONDS);
    
    #Currency Object Init
    coins = list(map(lambda coin : CurrencyQuery(coin), COINS));
    coinnames = map(lambda coin : coin.name, coins)
    map(lambda coin : coin.Refresh(), coins)
    prices = list(map(lambda coin : coin.GetPrice(), coins)) 
    
    priceUpdater = DataKeeper(coinnames, DATA_PATH)
    coinsHistory = priceUpdater.InitCoinsHistory(num, prices)
    
    while True:
        # update coin price
        map(lambda coin : coin.Refresh(), coins)
        # monitor 
        for i in range(len(coinsHistory)):
            queue = coinsHistory[i]
            queue.pop(0)
            queue.append(coins[i].GetPrice())
            rate = (queue[-1] - queue[0]) / (0.01+queue[0])
            if rate >= 0.05:
                coin = coins[i]
                body = ""+coin.name+" has increased upto " + str(rate * 100) + "% in the past " + str(HOUR) +" hour: $" + str(queue[0]) + "-> $" + str(queue[-1]);
                email.send_email(RECIPIENT, coin.name + ' price increased ' + "%.3f" % (rate*100) + '%', body) 
            elif rate <=-0.05:
                coin = coins[i]
                body = ""+coin.name+" has dropped downto " + str(rate * 100) + "% in the past " + str(HOUR) +" hour: $" + str(queue[0]) + "-> $" + str(queue[-1]);
                email.send_email(RECIPIENT, coin.name + ' price dropped '  + "%.3f" % (rate*100) + '%', body)
            
            osciliationRate = (max(queue) - min(queue)) / (0.01 + min(queue))
            if  osciliationRate > OSCILLATION_ALERT_THRESHOLD:
                coin = coins[i]
                body = ""+coin.name + " has  oscillated over " + str(osciliationRate*100) + " in the past " + str(HOUR) +" hour" + str(min(queue)) + "->$" + str(max(queue));
                email.send_email(RECIPIENT, coin.name + ' price oscillated over ' + "%.3f" % (osciliationRate*100) + "%", body)
        
        # Log price
        priceUpdater.LogPrice(map(lambda coin: coin.GetPrice(), coins))
        time.sleep(SLEEP_SECONDS)



#Coin object
class CurrencyQuery:
    def __init__(self, seed):
        self.seed = seed;
        self.name = self.seed[0]
        self.url=self.seed[1]
        self.Refresh()
    
    # Refresh, this call will lead to a network communication to:
    # 'http://coinmarketcap-nexuist.rhcloud.com/api'
    def Refresh(self):
        Errors.AssertEqual(len(self.seed), 2)
        self.resp, content = httplib2.Http().request(self.url)
        self.content = content.decode('ascii')
        self.OK = self.resp['status'] == '200'
        if self.OK:
            js = json.loads(self.content)
            self.USD = float(js['usd'])
        else:
            self.USD = 0
        
    # Return price
    def GetPrice(self):
        if self.OK:
            return self.USD
        else:
            raise Exception('Failed query with state code: ' + self.resp['status'])

#Currencies object
class AllCurrency:
    def __init__(self, jsonUrl):
        self.url = jsonUrl
        self.Refresh()
    
    def Refresh(self):
        self.resp, content = httplib2.Http().request(self.url)
        self.content = content.decode('ascii')
        self.OK = self.resp['status'] == '200'
        if self.OK:
            js = json.loads(self.content)
            self.currencyNames = js.keys()
        else:
            self.USD = 0
        
if __name__ == "__main__":
    main();
    #allCurrency = AllCurrency(ALLCURRENCY)
    #allCurrency.Refresh()
