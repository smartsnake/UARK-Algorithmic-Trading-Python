import alpaca_trade_api as tradeapi
import json
from time import sleep

class trading_bot():
    def __init__(self):
        passdata = None
        with open('../credentials/data.json') as json_file:
            data = json.load(json_file)
        self.alpaca = tradeapi.REST(data['API_KEY'], data['API_SECRET'], data['APCA_API_BASE_URL'], 'v2')
        self.account = self.alpaca.get_account()

    #Completes transactions such as buying and selling
    def submitOrder(self, quantity,company,side): # Ex. 1, "FB", "buy"
        time = self.alpaca.get_clock()
        if quantity > 0:
          try:
            self.alpaca.submit_order(
                symbol= company,
                qty= quantity,
                side= side,
                type= 'market',
                time_in_force= 'day',
            )
            print(f'Market order of |  {quantity} {company} {side}  | completed.')
            return True
          except:
            print(f'Order of | {quantity} {company}  {side} | did not go through.')
            return False
        else:
          print(f'Quantity is <=0, order of | {quantity} {company} {side} | not sent.');
          return True

    
    def sellAllCompanyStocks(self, company):
        spyPosition = None
        try:
            currentData = self.alpaca.get_position('SPY')
            spyPosition = currentData["qty"]
        except:
            spyPosition = 0
        self.submitOrder(spyPosition,company,"sell")
        print(f'***** All of {company} stocks have been sold *****')
    
    #Sells all shares
    def closeAllPositions(self):
        self.alpaca.closeAllPositions()
        print("***** All positions have been closed *****")
    
    def cancelAllPendingOrders(self):
        self.alpaca.cancelAllOrders()
        print("***** All pending orders have been canceled *****")
    