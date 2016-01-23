'''
Created on Nov 8, 2015

@author: zhuoli
'''
import csv
import datetime
import os.path

import ConsoleUtilities
from Errors import Log


# Read Write Currency price history from/to disk
class DataKeeper:
    
    DELIMITER = ','
    
    def __init__(self, coinnames, path):
        self.filename = path
        self.coinnames = coinnames
        
    def InitCoinsHistory(self, nums, prices):

        # Create csv file and write priceArray if it doesn't exist
        if not os.path.isfile(self.filename):

            # Feed rows
            rows = ['Date']
            coin_names = map(lambda name: name + " price $", self.coinnames)
            rows.extend(coin_names)

            # Write row title to csv file
            with open(self.filename, 'w') as csvfile:
                writer = csv.writer(csvfile, delimiter= DataKeeper.DELIMITER,
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(rows)
                ConsoleUtilities.WriteLine('Wrote header: ' + rows)

            # Return price array with the given price
            return [[price] * nums for price in prices]
        else:

            # If priceArray exists, read from csv file
            ConsoleUtilities.WriteLine('Data exists, reading priceArray from csv...')

            # Price array,
            # e.g: [BitCoin, LiteCoin, DogCoin] -> [[356.0,390.4, 420.5], [3.5, 3.4, 3.8], [0.00012, 0.00013, 0.00018]]
            priceArray = [[] for price in prices]

            # Open csv file
            with open(self.filename,'r') as csvfile:
                reader = csv.reader(csvfile, delimiter= DataKeeper.DELIMITER,
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)

                # Feed price cols
                for cols in reader:
                    try:
                        cols = list(map(lambda x: float(x), cols[1:]))
                        for idx in range(len(cols)):
                            priceArray[idx].append(cols[idx])
                    except ValueError:
                        Log("Invalid col format: " + "".join(cols))
            if len(priceArray[0]) < nums:
                for idx in range(len(prices)):
                    dif = nums - len(priceArray[idx])
                    head = [priceArray[idx][0]] * dif
                    head.extend(priceArray[idx])
                    priceArray[idx] = head
            elif len(priceArray[0]) > nums:
                diff = int(len(priceArray[0]) - nums)
                for idx in range(len(cols)):
                    priceArray[idx] = priceArray[idx][diff:]
            return priceArray;

    def LogPrice(self, coinprices):
        time = str(datetime.datetime.now())
        secondIndex = time.rfind(':')
        time = time[:secondIndex]
        rows = [time]
        rows.extend(coinprices)
        ConsoleUtilities.WriteLine(tuple(rows))
        with open(self.filename, 'a+') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(rows)