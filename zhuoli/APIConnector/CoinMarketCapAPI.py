import httplib2
import json
from APIConnector.APIConnectorBase import APIConnectorBase

BITCOIN = 'BitCoin'
LITECOIN = 'LITECOIN'
DOGECOIN = 'DogeCoin'


COINS = {
    BITCOIN  : "btc",
    LITECOIN : "ltc",
    DOGECOIN : "doge"
}


class CoinMarketCapAPI(APIConnectorBase):

    BASE_URL = 'http://coinmarketcap-nexuist.rhcloud.com/api'
    QUERRY_ELEMENT = 'price'

    def __init__(self):

        # Coin name-url pair
        self.nameUrlPairs = {
            BITCOIN:  CoinMarketCapAPI.BuildUpURL(COINS[BITCOIN]),
            LITECOIN: CoinMarketCapAPI.BuildUpURL(COINS[LITECOIN]),
            DOGECOIN: CoinMarketCapAPI.BuildUpURL(COINS[DOGECOIN])
        }

    # Splice to return the actual url
    def BuildUpURL(currencyName):
        return CoinMarketCapAPI.BASE_URL + '/' + currencyName + '/' + CoinMarketCapAPI.QUERRY_ELEMENT;

    # Get all goods names
    def GetAllGoodsNames(self):
        return list(self.nameUrlPairs.keys())

    # Retrieve price from SOAP API
    def RetrievePriceForGoods(self, goodsName):

        # Return -1 if goods not exist
        if goodsName not in self.nameUrlPairs:
            return -1

        requestUrl = self.nameUrlPairs[goodsName]
        resp, content = httplib2.Http().request(requestUrl)
        jsonResponse = content.decode('ascii')
        isOK = resp['status'] == '200'

        if isOK:
            js = json.loads(jsonResponse)
            return float(js['usd'])
        else:
            return -2
