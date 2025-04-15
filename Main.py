from ast import main
import numpy as np
import pandas as pd

import yfinance as yf
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from pandas.tseries.offsets import *
from datetime import datetime, date
import pickle
from functions import *
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

#defining path

aws_flag=False
if aws_flag:
    pass
else:
    current_directory = os.path.dirname(__file__)

model_file=os.path.join(current_directory,"LSTM_Models")
scale_file=os.path.join(current_directory,"LSTM_Scaler")
lstm_predicted_file=os.path.join(current_directory,'LSTM_Prediction')
scripts_to_run="Scripts_to_run.csv"
scripts_run="Scripts_run.csv"



def extract_data(ticker,Tickerfilepath):
    print(f"Storing 10 years data  of {ticker}")
    symbol=yf.Ticker(ticker)
    ticker_file= os.path.join(Tickerfilepath,ticker)
    ticker_data=symbol.history('10y')
    ticker_data.reset_index(inplace=True)
    ticker_data.to_csv(ticker_file+'.csv', index=False)


def read_file(tickername,Tickerfilepath):
    print(f'Reading file {tickername}')
    filepath = os.path.join(Tickerfilepath,tickername+'.csv')
    ticker_data=pd.read_csv(filepath,parse_dates=["Date"])
    ticker_data['Date']=ticker_data['Date'].dt.strftime('%Y-%m-%d')
    ticker_data.set_index('Date', inplace = True)
    ticker_data.sort_index(inplace = True)
    return ticker_data


if __name__ == "__main__":
    print(current_directory)
    filepath=os.path.join(current_directory,scripts_to_run)
    Scripts_to_run_pd=pd.read_csv(filepath)
    final_df=Scripts_to_run_pd.sort_values(by=['Priority'])
    listofticker=final_df.loc[final_df['Model_created']=='No','Symbol'].to_list()
    initial_list=[]
    initial_list=listofticker[0:1]
    Tickerfilepath=os.path.join( current_directory,"TickerFiles")
    for x in initial_list:
        extract_data(ticker=x,Tickerfilepath=Tickerfilepath)
        ticker=read_file(x,Tickerfilepath=Tickerfilepath)
        print(f"Modelling of {x} is starting")
        model, scaler_fit, X_test, shape_x, prediction_start,y_pred_transform=create_model(ticker)
        print(f"Modelling of {x} is finished")
        model_name = os.path.join(model_file , x + ".keras")
        print(model_name)
        model.save(model_name)
        print(f"Model of {x} is saved")
        scaler_name=os.path.join(scale_file , x + ".pickle")
        with open(scaler_name,'wb') as f:
            pickle.dump(scaler_fit,f)
        result = create_file(ticker)
        result=update_file(result,y_pred_transform)
        result=add_new_dates(result)
        print(f"Predicting values of {x} ")
        result=upload_data(result,X_test,shape_x,scaler_fit,model,prediction_start)
        result=update_file_after_prediction(result)
        result.to_csv(os.path.join(lstm_predicted_file,x+".csv"))
        print(f"Processing of {x} is complete")
        final_df.loc[final_df['Symbol'] == x, 'Model_created'] = 'Yes'
    final_df.to_csv(scripts_run,index=False)
    
