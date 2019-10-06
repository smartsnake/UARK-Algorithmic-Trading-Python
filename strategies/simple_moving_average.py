import alpaca_trade_api as tradeapi
import json
from src.trading_bot import trading_bot
from src.market_data import market_data


debug = True

class simple_moving_average():
    def __init__(self):

        data = None
        with open('./credentials/data.json') as json_file:
            data = json.load(json_file)
        self.alpaca = tradeapi.REST(data['API_KEY'], data['API_SECRET'], data['APCA_API_BASE_URL'], 'v2')

    def getAverage(self, dataArray):
        Total = 0
        Avg = 0
        for element in dataArray:
            Total += element
        Avg = (Total/len(dataArray))
        return Avg

    def run(self):
        while True:
            if debug:
                print('Working...')

            #/*******************************************************
            #Checking to make sure the market is open!
            #********************************************************/
            time = self.alpaca.get_clock()
            if not time.is_open:
               print('Not Open!')
               break
            
            # /*******************************************************
            # Gets the Number a Shares of SPY and OrderSize
            # ********************************************************/
            spyPosition = None
            try:
                currentData = self.alpaca.get_position('SPY')
                spyPosition = currentData["qty"]
            except:
                spyPosition = 0

            if debug:
                print(f'spyPosition: {spyPosition}')
            
            #Gets Account Information
            account = self.alpaca.get_account()
            #Setting the position Size to 10% of portfolio
            positionSize = account['portfolio_value'] * .1
            print(f'Position Size: {positionSize}')
            #Get the current Price of SPY to figure out the amount of shares we need to purchuse
            currentPrice  = market_data.getPrice("minute",'SPY',1,"o")
            #Setting the Order Size (Number of shares)
            shareOrderSize = int(positionSize / currentPrice[0])
            print(f'Share order size: {shareOrderSize}')

            # /*******************************************************
            # Setting the 15 min Moving Average and the 30min Moving Average
            # *******************************************************/
            #Part 1 (15 min Average)
            #Calculating the 15min moving average as MA15Avg
            MA15  = market_data.getPrice("minute",'SPY',15,"o")
            MA15Avg = self.getAverage(MA15)
    
            #Part 2 (30 min Average)
            #Calculating the 30min moving average as MA30Avg
            MA30  = market_data.getPrice("minute",'SPY',30,"o")
            MA30Avg = self.getAverage(MA30)
            if debug:
                print(f'MA15 = {MA15Avg}')
                print(f'MA30 = {MA30Avg}')
                print(f'MA15Avg > MA30Avg: {MA15Avg>MA30Avg}')
            
            # /***************************************************
            # Buy/Sell logic
            # ****************************************************/
            #if there is no postion in SPY we need to open one
            if spyPosition == 0 :
                if(MA15Avg>MA30Avg):#if MA15 greater than MA30 buy 10% of portfolio
                    trading_bot.submitOrder(shareOrderSize,"SPY","buy")
                else:
                    trading_bot.submitOrder(shareOrderSize,"SPY","sell")
            
            #If we have a postive number of shares of SPY (Meaning we are already long)    
            elif spyPosition > 0:
                if MA15Avg<MA30Avg:
                    # 1) Close Current Position
                    trading_bot.sellAllCompanyStocks("SPY")
                    # 2) Open a Short Position with 10% of portfolio
                    trading_bot.submitOrder(shareOrderSize,"SPY","sell")
            
            #If we have a negative number of shares of SPY (Meaning we are alreday short)    
            elif spyPosition < 0:
                if MA15Avg>MA30Avg:
                    # 1) Close Current Position
                    trading_bot.sellAllCompanyStocks("SPY")
                    # 2) Open a Long Position with 10% of portfolio
                    trading_bot.submitOrder(shareOrderSize,"SPY","buy")
                
            
                
            





            