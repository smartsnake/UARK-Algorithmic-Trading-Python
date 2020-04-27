import alpaca_trade_api as tradeapi
import json
from src.trading_bot import trading_bot
from src.market_data import market_data
from time import sleep


debug = True
Trading = True

class exponential_moving_average():

    def __init__(self):

        self.smoothing = 2

        data = None
        with open('./credentials/data.json') as json_file:
            data = json.load(json_file)
        self.alpaca = tradeapi.REST(data['API_KEY'], data['API_SECRET'], data['APCA_API_BASE_URL'], 'v2')

        self.market_data = market_data()
        self.trading_bot = trading_bot()
        
    def __str__(self):
        return 'exponential_moving_average'

    def getAverage(self, dataArray):
        Total = 0
        Avg = None
        for element in dataArray:
            Total += element
        Avg = (Total/len(dataArray))
        return Avg


    def getEMA(self, data, k):
        if(len(data) == 1):
            return float(data[0])
        EMA_Final = (int(data[0]) * k + self.getEMA(data[:-1], k) * (1 - k))
        return EMA_Final


    def run(self):
        while True:
            if debug:
                print('Working...')
            sleep(2)#wait 2 seconds
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
            currentPrice  = self.market_data.getPrice(barDuration='minute',symbol='SPY',pastDays=1,dataType='o')
            #Setting the Order Size (Number of shares)
            if debug:
                print(f'current price: {currentPrice}')
            shareOrderSize = int(positionSize / currentPrice[0])
            print(f'Share order size: {shareOrderSize}')

            # /*******************************************************
            # Setting the 15 min Moving Average and the 30min Moving Average
            # *******************************************************/
            #Part 1 (15 min Average)
            #Calculating the 15min moving average as MA15Avg
            MA15  = self.market_data.getPrice("minute",'SPY',15,"o")
            
            k = self.smoothing/(len(MA15) + 1)
            MA15EMA = self.getEMA(MA15, k)
    
            #Part 2 (30 min Average)
            #Calculating the 30min moving average as MA30Avg
            MA30  = self.market_data.getPrice("minute",'SPY',30,"o")

            k = self.smoothing/(len(MA30) + 1)
            MA30EMA = self.getEMA(MA30, k)

            if debug:
                #print(f'MA15 data: {MA15}')
                print(f'MA15 = {MA15EMA}')
                #print(f'MA10 data: {MA30}')
                print(f'MA30 = {MA30EMA}')
                print(f'MA15EMA > MA30EMA: {MA15EMA>MA30EMA}')
            
            # /***************************************************
            # Buy/Sell logic
            # ****************************************************/
            #if there is no postion in SPY we need to open one
            if Trading:
                if spyPosition == 0 :
                    if(MA15EMA>MA30EMA):#if MA15 greater than MA30 buy 10% of portfolio
                        self.trading_bot.submitOrder(quantity=shareOrderSize,company="SPY", side="buy")
                    else:
                        self.trading_bot.submitOrder(quantity=shareOrderSize,company="SPY", side="sell")
                
                #If we have a postive number of shares of SPY (Meaning we are already long)    
                elif spyPosition > 0:
                    if MA15EMA<MA30EMA:
                        # 1) Close Current Position
                        self.trading_bot.sellAllCompanyStocks("SPY")
                        # 2) Open a Short Position with 10% of portfolio
                        self.trading_bot.submitOrder(quantity=shareOrderSize,company="SPY", side="sell")
                
                #If we have a negative number of shares of SPY (Meaning we are alreday short)    
                elif spyPosition < 0:
                    if MA15EMA>MA30EMA:
                        # 1) Close Current Position
                        self.trading_bot.sellAllCompanyStocks(company="SPY")
                        # 2) Open a Long Position with 10% of portfolio
                        self.trading_bot.submitOrder(quantity=shareOrderSize,company="SPY", side="buy")
            