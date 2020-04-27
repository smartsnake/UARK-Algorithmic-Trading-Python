import alpaca_trade_api as tradeapi
import json
from src.trading_bot import trading_bot
from src.market_data import market_data
from time import sleep


def getAverage(dataArray):
    Total = 0
    Avg = None
    for element in dataArray:
        Total += element
    Avg = (Total/len(dataArray))
    return Avg

def EMA(data, k):
    #print(f'data: {data}, k: {k}')
    if(len(data) == 1):
        return float(data[0])
    #EMA_Final = None
    #for element in data:
    EMA_Final = (int(data[0]) * k + EMA(data[:-1], k) * (1 - k))
    return EMA_Final

#Init
data = None
with open('./credentials/data.json') as json_file:
    data = json.load(json_file)

alpaca = tradeapi.REST(data['API_KEY'], data['API_SECRET'], data['APCA_API_BASE_URL'], 'v2')
market_data = market_data()
trading_bot = trading_bot()

#Testing
account = alpaca.get_account()
print(f'account: {account}')

#currentData = alpaca.get_position('SPY')
#print(f'current data: {currentData}')

#Calculating the 15min moving average as MA15Avg
MA15  = market_data.getPrice("minute",'SPY',15,"o")
print(f'SPY 15 data: {MA15}')

MA30  = market_data.getPrice("minute",'SPY',30,"o")
print(f'SPY 30 data: {MA30}')


#testing EMA 15
#print(f'len: {len(test_data)}')
EMA_15 = EMA(MA15, (2/(len(MA15) + 1)))
print(f'EMA 15: {EMA_15}')

#testing EMA 30
EMA_30 = EMA(MA30, (2/(len(MA30) + 1)))
print(f'EMA 30: {EMA_30}')