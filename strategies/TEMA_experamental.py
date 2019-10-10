import alpaca_trade_api as tradeapi
import json
import pandas as pd
import numpy as np
from src.trading_bot import trading_bot
from src.market_data import market_data
from time import sleep


debug = True
Trading = True

class TEMA_experamental():
    def __init__(self):
        data = None
        with open('./credentials/data.json') as json_file:
            data = json.load(json_file)
        self.alpaca = tradeapi.REST(data['API_KEY'], data['API_SECRET'], data['APCA_API_BASE_URL'], 'v2')

        self.market_data = market_data()
        self.trading_bot = trading_bot()
    def __str__(self):
        return 'TEMA_experamental'

    def getAverage(self, dataArray):
        Total = 0
        Avg = None
        for element in dataArray:
            Total += element
        Avg = (Total/len(dataArray))
        return Avg

    #Using https://www.investopedia.com/ask/answers/122314/what-exponential-moving-average-ema-formula-and-how-ema-calculated.asp
    #for calculating EMA
    def calEMA(self, currentPrice, prevPrice, period):
        
        k = 2/(period + 1)
        ema = currentPrice * k + self.calEMA(prevPrice) * (1-k)
        return ema

    def ema(self, s, n):
        """
        returns an n period exponential moving average for
        the time series s

        s is a list ordered from oldest (index 0) to most
        recent (index -1)
        n is an integer

        returns a numeric array of the exponential
        moving average
        """
        s = np.array(s)
        ema = []
        j = 1

        #get n sma first and calculate the next n period ema
        sma = sum(s[:n]) / n
        multiplier = 2 / float(1 + n)
        ema.append(sma)

        #EMA(current) = ( (Price(current) - EMA(prev) ) x Multiplier) + EMA(prev)
        ema.append(( (s[n] - sma) * multiplier) + sma)

        #now calculate the rest of the values
        for i in s[n+1:]:
            tmp = ( (i - ema[j]) * multiplier) + ema[j]
            j = j + 1
            ema.append(tmp)

        return ema
    
    def run(self):
        while True:
            if debug:
                print('Working...')
            sleep(1)#wait 1 seconds
            #/*******************************************************
            #Checking to make sure the market is open!
            #********************************************************/
            time = self.alpaca.get_clock()
            if not time.is_open:
               print('Not Open!')
               self.market_data.waitForMarketToOpen()
               ##break

            # /*******************************************************
            # Gets the Number a Shares of SPY and OrderSize
            # ********************************************************/
            spyPosition = None
            try:
                currentData = self.alpaca.get_position('SPY')
                spyPosition = int(currentData.qty)
            except:
                print('------------EXCEPT---------------------')
                spyPosition = 0

            if debug:
                print(f'spyPosition: {spyPosition}')


            #Gets Account Information
            #Setting the position Size to 10% of portfolio
            positionSize = int(float(self.alpaca.get_account().equity) * 0.1)
            print(f'Position Size: {positionSize}')
            #Get the current Price of SPY to figure out the amount of shares we need to purchuse
            currentPrice  = self.market_data.getPrice(barDuration='minute', symbol='SPY', pastDays=1, dataType='o')
            #Setting the Order Size (Number of shares)
            if debug:
                print(f'current price: {currentPrice}')
            shareOrderSize = int(positionSize / currentPrice[0])
            print(f'Share order size: {shareOrderSize}')


            # /*******************************************************
            # Setting the 20 min Exp Moving Average and the 30min Exp Moving Average
            # *******************************************************/
            MA20  = self.market_data.getPrice("1Min",'SPY',20,"o")
            MA20DF = pd.DataFrame(MA20)
            MA20Avg = MA20DF.ewm(span=len(MA20DF), adjust=False).mean()

            MA20Avg = MA20Avg[0][len(MA20Avg) - 1]
    
            #Part 2 (30 min Average)
            #Calculating the 100 moving average as MA30Avg
            MA100  = self.market_data.getPrice("1Min",'SPY',100,"o")
            MA100DF = pd.DataFrame(MA100)
            MA100Avg = MA100DF.ewm(span=len(MA100DF), adjust=False).mean()

            MA100Avg = MA100Avg[0][len(MA100Avg) - 1]

            MA20EMA = self.ema(MA20, len(MA20) - 1)
            MA100EMA = self.ema(MA100, len(MA100) - 1)

            if debug:
                print(f'MA20 pd = {MA20Avg}')
                print(f'MA20 ema = {MA20EMA}')
                print(f'MA100 pd = {MA100Avg}')
                print(f'MA100 ema = {MA100EMA}')
                
                #print(f'MA20Avg > MA100Avg: {MA20Avg > MA100Avg}')
            break
