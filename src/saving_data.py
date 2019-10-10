import pandas as pd
from os import path

SAVE_DIR = 'SAVES'
FILE_NAME = f'MASTER_LOGS.csv'

class saving_data():


    def __init__(self):
        if not path.exists(SAVE_DIR):
            path.mkdir(SAVE_DIR)

    def load_existing_logs(self):
        with open(FILE_NAME) as MASTER_LOGS:
            df = pd.read_csv(FILE_NAME)
            return df
    
    def saveFrame(self, marketData, quantity, company, side, algo):

        master_logs = self.load_existing_logs()

        temp_list = [element for element in marketData]
        temp_list.extend([quantity, company, side])
        #df = pd.DataFrame(data=temp_list)
        
        master_logs.append(temp_list)
