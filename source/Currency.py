__author__ = 'zhuoli'

import httplib2
import json
import Errors
import datetime

# Represents an digit currency
class Currency:

    def __init__(self, currencyQuery, dateArray, priceArray):

        self.name = currencyQuery.name
        self.currencyQuery = currencyQuery
        Errors.AssertEqual(len(dateArray), len(priceArray))

        # e.g:
        # [
        #   ['2015.11.12', '2015.11.13', '2015.11.14'],
        #   [        3.5,          4.5,          4.7]
        # ]
        self.datePricePairs = [dateArray, priceArray]
        self.priceArray =  priceArray
        self.dateArray  = dateArray
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
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.Refresh()
        self.queryContent = ""
        self.USD = 0

    # Refresh, this call will lead to a network communication to:
    # 'http://coinmarketcap-nexuist.rhcloud.com/api'
    def Refresh(self):
        resp, content = httplib2.Http().request(self.url)
        self.queryContent = content.decode('ascii')
        isOK = resp['status'] == '200'
        if isOK:
            js = json.loads(self.queryContent)
            self.USD = float(js['usd'])
        else:
            self.USD = 0

    # Return price
    def GetPrice(self):

        # Retrieve Price if hasn't
        if self.USD == 0:
            self.Refresh()
        return self.USD
