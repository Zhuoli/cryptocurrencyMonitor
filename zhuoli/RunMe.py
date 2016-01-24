'''
Digit Currency Monitor - V1.0
Created on Nov 8, 2015

@author: zhuoli
'''
import json
import os
import sys
import time
import  datetime
import traceback

import httplib2

import ConsoleUtilities
import Constant
from DataKeeper import DataKeeper
from Email import Email
from Errors import Log
from Currency import Currency
from Currency import CurrencyQuery


DATA_PATH = Constant.DATA_ROOT + '/priceLog.csv'

BITCOIN = 'BitCoin'
LITECOIN = 'LITECOIN'
DOGECOIN = 'DogeCoin'

COINS = {
        BITCOIN  : "http://coinmarketcap-nexuist.rhcloud.com/api/btc/price",
        LITECOIN : "http://coinmarketcap-nexuist.rhcloud.com/api/ltc/price",
        DOGECOIN : "http://coinmarketcap-nexuist.rhcloud.com/api/doge/price"
        }

BUYPRICE = {
        BITCOIN : 350,
        LITECOIN : 3.10,
        DOGECOIN : 0.00133941
}

SELLPRICE = {
        BITCOIN : 440,
        LITECOIN : 3.5,
        DOGECOIN : 1.8
}

RECIPIENT = 'zhuoliseattle@gmail.com'
SLEEP_SECONDS = 10 * 60 # Refresh price interval
HOUR = 8 # Monitor interval
MONITOR_WINDOW = HOUR * 60 * 60 # 1 hours monitor history

# When should consider buy coins
SELL_ALERT_THRESHOLD = 0.05

# When should consider sell coins
BUY_ALERT_THRESHOLD = 0.05

# Alert for oscillation
OSCILLATION_ALERT_THRESHOLD = 0.1

# Email interval
EMAIL_INTERVAL = 30 * 60 # 30 minutes

def main():

    LastTimeSendEmail = datetime.datetime.min

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

# Monitor the real time currency
def Monitor(email):


    num = int(MONITOR_WINDOW / SLEEP_SECONDS);
    
    #Currency Object Init
    coins = []
    for coinPair in COINS.items():
        coins.append(CurrencyQuery(coinPair))

    coinnames = list(map(lambda coin : coin.name, coins))
    map(lambda coin : coin.Refresh(), coins)

    # Retrieve current coin price from APIs
    prices = list(map(lambda coin : coin.GetPrice(), coins)) 

    # Retrieve history coin price from disk csv file
    CSVReader = DataKeeper(coinnames, DATA_PATH)
    coinsHistoryArray, dateArray = CSVReader.InitCoinsHistory(num, prices)

    currencyList = []
    for idx in range(len(coinnames)):
        currencyList.append(Currency(COINS, coinnames[idx], (dateArray, coinsHistoryArray[idx])))


    DailyEmailDate = datetime.datetime.min
    while True:

        # Analysis
        for currencyInstance in currencyList:

            # update coin price
            currencyInstance.UpdatePrice();

        # Daily Price email
        if DailyEmailDate.day != datetime.datetime.now().day:
            DailyEmailDate = datetime.datetime.now()
            body = ""
            for currencyInstance in currencyList:
                body += '\n' + currencyInstance.name + " : " + str(currencyInstance.latestPrice)
            email.send_email(RECIPIENT, "Daily Price Report", body)

        # Suggest to sell


        # Suggest to buy


        # Analysis
        for i in range(len(coinsHistoryArray)):
            queue = coinsHistoryArray[i]
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
        CSVReader.LogPrice(map(lambda coin: coin.GetPrice(), coins))
        time.sleep(SLEEP_SECONDS)

if __name__ == "__main__":
    main();
    #allCurrency = AllCurrency(ALLCURRENCY)
    #allCurrency.Refresh()
