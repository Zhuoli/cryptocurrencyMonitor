__author__ = 'zhuoli'

class APIConnectorBase:

    def __init__(self):
        ...

    def BuildUpURL(self, url):
        ...

    def GetAllGoodsNames(self):
        ...

    def RetrievePriceForGoods(self, goodsName):
        ...