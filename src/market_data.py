import alpaca_trade_api as tradeapi
import json
from time import sleep

class market_data():
    def __init__(self):
        data = None
        with open('./credentials/data.json') as json_file:
            data = json.load(json_file)
        self.alpaca = tradeapi.REST(data['API_KEY'], data['API_SECRET'], data['APCA_API_BASE_URL'], 'v2')
    
    def getPrice(self, barDuration, symbol, pastDays, dataType): #barDuration = 'minute' | '1Min' | '5Min' | '15Min' | 'day' | '1D' ______ dataType = "t" | "o" | "h" | "l" | "c" | "v"
        price = self.alpaca.get_barset(symbol, barDuration, limit = pastDays)
        desiredData = price[symbol]
        #print(f'data: {desiredData}')
        dataArray = []
        for element in desiredData:
            dataArray.append(element.o)
        #print(f'dataArray: {dataArray}')
        return dataArray
    
    def getShares(self, symbol):
        Position = self.alpaca.get_position(symbol)
        return Position 

    def waitForMarketToOpen(self):
        while True:
            time = self.alpaca.get_clock()
            sleep(10)#10 seconds
            if time.is_open:
                print("****** Market is Open ******")
                break
            print("-- Waiting for market to open --")
    