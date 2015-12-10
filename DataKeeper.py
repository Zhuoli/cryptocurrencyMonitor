'''
Created on Nov 8, 2015

@author: zhuoli
'''
import os.path
import csv
import datetime
from Errors import Log
class DataKeeper:
    
    DELIMITER = ','
    
    def __init__(self, coinnames, path):
        self.filename = path
        self.coinnames = coinnames
    
    
    def InitCoinsHistory(self, nums, prices):
        if not os.path.isfile(self.filename):
            rows = ['Date']
            coinnames = map(lambda name : name+" price $",self.coinnames)
            rows.extend(coinnames)
            with open(self.filename, 'w') as csvfile:
                writer = csv.writer(csvfile, delimiter= DataKeeper.DELIMITER,
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(rows)
                print 'Wrote header: ',
                print rows 
            return [[price] * nums for price in prices]
        else:
            print 'Data exists, reading data from csv...'
            data = [[] for price in prices]
            with open(self.filename,'r') as csvfile:
                reader = csv.reader(csvfile, delimiter= DataKeeper.DELIMITER,
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
                for cols in reader:
                    try:
                        cols = map(lambda x: float(x), cols[1:])
                        for idx in range(len(cols)):
                            data[idx].append(cols[idx])
                    except ValueError:
                        Log("Invalid col format: " + "".join(cols))
            if len(data[0]) < nums:
                for idx in range(len(prices)):
                    dif = nums - len(data[idx])
                    head = [data[idx][0]] * dif
                    head.extend(data[idx])
                    data[idx] = head
            elif len(data[0]) > nums:
                diff = len(data[0]) - nums
                for idx in range(len(cols)):
                    data[idx] = data[idx][diff:]
            return data;

    def LogPrice(self, coinprices):
        time = str(datetime.datetime.now())
        secondIndex = time.rfind(':')
        time = time[:secondIndex]
        rows = [time]
        rows.extend(coinprices)
        print rows
        with open(self.filename, 'a+') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(rows)