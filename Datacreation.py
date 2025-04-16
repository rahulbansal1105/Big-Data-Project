import numpy as np
import pandas as pd

import yfinance as yf
import os

from datetime import datetime, date




aws_flag=False
if aws_flag:
    pass
else:
    current_directory = os.path.dirname(__file__)

list_of_files="NSE Data.csv"

def extract_data(ticker,Tickerfilepath):
    print(f"Storing 10 years data  of {ticker}")
    symbol=yf.Ticker(ticker)
    ticker_file= os.path.join(Tickerfilepath,ticker)
    ticker_data=symbol.history('10y')
    ticker_data.reset_index(inplace=True)
    ticker_data.to_csv(ticker_file+'.csv', index=False)

if __name__ == "__main__":
    print(current_directory)
    #filepath=os.path.join(current_directory,list_of_files)
    #list_of_files_pd=pd.read_csv(filepath)
    #listofticker=list_of_files_pd.loc[list_of_files_pd['Model_created']=='No','Symbol'].to_list()
    #Tickerfilepath=os.path.join( current_directory,"NSE DATA")
    #print(f" list of file is {listofticker}")
    #for x in listofticker:
    #    extract_data(ticker=x,Tickerfilepath=Tickerfilepath)
    #print("Process finished")
    # Iterate through all files in the folder
    folder_path=os.path.join( current_directory,"NSE DATA")
    folder_path_2=os.path.join( current_directory,"all_data.csv")
    folder_path_3=os.path.join( current_directory,"list_of_ids.csv")

    combined_data = pd.DataFrame(columns=['id','datetime','value'])
    list_of_ids = pd.DataFrame( columns=['filename','id'])
    counter = 1001
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        
        # Check if it's a file (not a directory)
        if os.path.isfile(file_path):
            print(f"Reading file: {file_name}")
            
            # Example: Read CSV files
            if file_name.endswith('.csv'):
                data = pd.read_csv(file_path,parse_dates=["Date"])
                data['datetime'] =  data['Date'].astype('int64') // 10**9
                data['id'] = counter
                final_data = data[['id','datetime','Close']].rename( columns={'Close':'value'})
                combined_data=pd.concat([combined_data,final_data],ignore_index=True)
                new_row = {'filename': file_name, 'id': counter }
                list_of_ids = pd.concat([list_of_ids, pd.DataFrame([new_row])], ignore_index=True)
                counter +=1
    combined_data.to_csv(folder_path_2,index=False)
    list_of_ids.to_csv(folder_path_3,index=False)

  