__author__ = 'zhuoli'

import httplib2
import json
import Errors
import datetime

# Represents an digit currency
class Currency:

    def __init__(self, NameUrlPairs, name, priceArrayPair):

        self.name = name
        self.currencyQuery = CurrencyQuery((name,NameUrlPairs[name]))
        Errors.AssertEqual(len(priceArrayPair[0]), len(priceArrayPair[1]))

        # e.g:
        # [
        #   ['2015.11.12', '2015.11.13', '2015.11.14'],
        #   [        3.5,          4.5,          4.7]
        # ]
        self.datePricePairs = [priceArrayPair[0], priceArrayPair[1]]
        self.priceArray = self.datePricePairs[1]
        self.dateArray  = self.datePricePairs[0]
        self.latestPrice = self.currencyQuery.GetPrice();

    def UpdatePrice(self):
        self.currencyQuery.Refresh()
        self.latestPrice = self.currencyQuery.USD

        # Append current price
        self.priceArray.append(self.latestPrice)

        # Append current time
        time = str(datetime.datetime.now())
        # Trim
        secondIndex = time.rfind(':')
        time = time[:secondIndex]
        self.dateArray.append(time);

    def GetLatestPrice(self):
        return self.latestPrice;






#Coin object
class CurrencyQuery:
    def __init__(self, seed):
        Errors.AssertEqual(len(seed), 2)
        self.NameUrlPair = seed;
        self.name = self.NameUrlPair[0]
        self.url=self.NameUrlPair[1]
        self.Refresh()

    # Refresh, this call will lead to a network communication to:
    # 'http://coinmarketcap-nexuist.rhcloud.com/api'
    def Refresh(self):
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
