
'''
Created on Nov 8, 2015

@author: zhuoli
'''
import csv
import datetime
import os.path

import ConsoleUtilities
from Errors import Log
from Currency import Currency


# Read Write Currency price history from/to disk
class DataKeeper:
    
    DELIMITER = ','
    
    def __init__(self, coinnames, path):
        self.filename = path
        self.coinnames = coinnames


    # Initit coins history
    # Return price 2D array,
    # e.g:
    # Price array,
    # e.g: [BitCoin, LiteCoin, DogCoin]
    # ->
    # [
    #  [356.0,    390.4,   420.5],
    #  [  3.5,      3.4,     3.8],
    #  [0.0012, 0.00013, 0.00018]
    # ]
    def InitCoinsHistory(self, numberOfRowsForAnalysis, prices):

        numberOfRowsForAnalysis = int(numberOfRowsForAnalysis)

        dateArray = []

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
                ConsoleUtilities.WriteLine('Wrote header: ' + "".join(rows))

            # Return price array with the given price
            return [[price] * numberOfRowsForAnalysis for price in prices]
        else:

            # If priceArray exists, read from csv file
            ConsoleUtilities.WriteLine('Data exists, reading priceArray from csv...')

            # Price array,
            # e.g: [BitCoin, LiteCoin, DogCoin]
            # ->
            # [
            #  [356.0,    390.4,   420.5],
            #  [  3.5,      3.4,     3.8],
            #  [0.0012, 0.00013, 0.00018]
            # ]
            price2DArray = [[] for price in prices]

            # Open csv file
            with open(self.filename,'r') as csvfile:
                reader = csv.reader(csvfile, delimiter= DataKeeper.DELIMITER,
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)

                # Feed price cols
                for csvRow in reader:
                    try:
                        # Remove the date col and convert string to float
                        priceRow = list(map(lambda x: float(x), csvRow[1:]))

                        # Record this date
                        dateArray.append(csvRow[0])

                        # Append the currency price
                        for idx in range(len(priceRow)):
                            price2DArray[idx].append(priceRow[idx])
                    except ValueError:
                        Log("Invalid col format: " + "".join(csvRow))

            return price2DArray, dateArray;

    # Clean up the 2D currency array
    def FillTheMissingCurrencyArray(self, priceArray, numberOfRowsForAnalysis, currentPrices):

        # If the price 2D array doesn't contain enough records for analysis, we fill it with current price
        if len(priceArray[0]) < numberOfRowsForAnalysis:

            # Iterate each currency
            for idx in range(len(currentPrices)):
                dif = numberOfRowsForAnalysis - len(priceArray[idx])
                head = [currentPrices[idx]] * dif
                head.extend(priceArray[idx])
                priceArray[idx] = head

        # If the price 2D array exceed the number of rows for analysis, we truncate it
        elif len(priceArray[0]) > numberOfRowsForAnalysis:
            diff = int(len(priceArray[0]) - numberOfRowsForAnalysis)
            for idx in range(len(currentPrices)):
                priceArray[idx] = priceArray[idx][diff:]
        return priceArray;

    # Write the coin price row to CSV file
    def LogPrice(self, currencyList):

        prices = []
        for currencyInstance in currencyList:
            prices.append(currencyInstance.latestPrice)

        # Append current time
        time = str(datetime.datetime.now())

        # Trim
        secondIndex = time.rfind(':')
        time = time[:secondIndex]
        rows = [time]

        # Combine time and prices
        rows.extend(prices)
        ConsoleUtilities.WriteLine(tuple(rows))

        # Write
        with open(self.filename, 'a+') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(rows)


class CSVManager:

    DELIMITER = ','
    
    def __init__(self, coinnames, path):
        self.filename = path

    def Read(self, startRow, startCol):
        result = [[]]

        # Return empty array if path not exist
        if not os.path.isfile(self.filename):
            return result

        # Open csv file
        with open(self.filename,'r') as csvfile:
            reader = csv.reader(csvfile, delimiter= DataKeeper.DELIMITER,
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)

            # Return empty array if data is empty
            if len(reader) == 0 or len(reader[0]) == 0:
                return result;

            Data2DArray = self.RrverseAntiClockWise90Degree(reader)
            Data2DArray = self.ReverseOrder(Data2DArray)

            result = Data2DArray[startCol : [startRow]]
            return result

    def RrverseAntiClockWise90Degree(self, TwoDArray):

        for row in range(len(TwoDArray)):
            for col in range(row, len(TwoDArray[row])):
                TwoDArray[row][col], TwoDArray[col][row] = TwoDArray[col][row], TwoDArray[row][col]

        TwoDArray = TwoDArray[::-1]
        return TwoDArray


arr = [1,2,3]
manager = CSVManager('','')




