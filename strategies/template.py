import alpaca_trade_api as tradeapi
import json
from src.trading_bot import trading_bot
from src.market_data import market_data
from time import sleep


debug = True
Trading = True

class TEMPLATE():

    def __init__(self):

        data = None
        with open('./credentials/data.json') as json_file:
            data = json.load(json_file)
        self.alpaca = tradeapi.REST(data['API_KEY'], data['API_SECRET'], data['APCA_API_BASE_URL'], 'v2')

        self.market_data = market_data()
        self.trading_bot = trading_bot()
        
    def __str__(self):
        return 'TEMPLATE'

    def run(self):
        while True:
            if debug:
                print('Working...')
            sleep(2)#wait 2 seconds
            