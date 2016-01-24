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
SLEEP_SECONDS = 3 #10 * 60 # Refresh price interval
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

    coinnames = [BITCOIN, LITECOIN, DOGECOIN]

    # Init coin instances
    coins = [
        CurrencyQuery(BITCOIN, COINS[BITCOIN]),
        CurrencyQuery(LITECOIN, COINS[LITECOIN]),
        CurrencyQuery(DOGECOIN, COINS[DOGECOIN])
    ]

    # Retrieve current coin price from APIs
    prices = list(map(lambda coin : coin.GetPrice(), coins)) 

    # Retrieve history coin price from disk csv file
    CSVReader = DataKeeper(coinnames, DATA_PATH)
    coinsHistoryArray, dateArray = CSVReader.InitCoinsHistory(num, prices)

    currencyList = [

        Currency(coins[0], dateArray, coinsHistoryArray[0]),
        Currency(coins[1], dateArray, coinsHistoryArray[1]),
        Currency(coins[2], dateArray, coinsHistoryArray[2])
    ]

    DailyEmailDate = datetime.datetime.min
    while True:

        # Daily Price email
        if DailyEmailDate.day != datetime.datetime.now().day:
            DailyEmailDate = datetime.datetime.now()
            body = ""
            for currencyInstance in currencyList:
                body += '\n' + currencyInstance.name + " : " + str(currencyInstance.latestPrice)
            email.send_email(RECIPIENT, "Daily Price Report", body)

        # Analysis
        for currencyInstance in currencyList:

            # update coin price
            currencyInstance.UpdatePrice();
            rate = (currencyInstance.priceArray[-1] - currencyInstance.priceArray[0]) / (0.01 + currencyInstance.priceArray[0])

            if rate >= 0.05:
                body = ""+currencyInstance.name+" has increased upto " + str(rate * 100) + "% in the past " + str(HOUR) +" hour: $" + str(currencyInstance.priceArray[0]) + "-> $" + str(currencyInstance.latestPrice);
                email.send_email(RECIPIENT, currencyInstance.name + ' price increased ' + "%.3f" % (rate*100) + '%', body)
            elif rate <=-0.05:
                body = ""+currencyInstance.name+" has dropped downto " + str(rate * 100) + "% in the past " + str(HOUR) +" hour: $" + str(currencyInstance.priceArray[0]) + "-> $" + str(currencyInstance.latestPrice);
                email.send_email(RECIPIENT, currencyInstance.name + ' price dropped '  + "%.3f" % (rate*100) + '%', body)

            osciliationRate = (max(currencyInstance.priceArray) - min(currencyInstance.priceArray)) / (0.01 + min(currencyInstance.priceArray))
            if  osciliationRate > OSCILLATION_ALERT_THRESHOLD:
                body = ""+currencyInstance.name + " has  oscillated over " + str(osciliationRate*100) + " in the past " + str(HOUR) +" hour" + str(min(currencyInstance.priceArray)) + "->$" + str(max(currencyInstance.priceArray));
                email.send_email(RECIPIENT, currencyInstance.name + ' price oscillated over ' + "%.3f" % (osciliationRate*100) + "%", body)
        # Suggest to sell


        # Suggest to buy



        # Log price
        CSVReader.LogPrice(currencyList)
        time.sleep(SLEEP_SECONDS)

if __name__ == "__main__":
    main();
    #allCurrency = AllCurrency(ALLCURRENCY)
    #allCurrency.Refresh()
