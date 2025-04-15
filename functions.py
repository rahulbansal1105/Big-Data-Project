import numpy as np
import pandas as pd
import tensorflow as tf
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from pandas.tseries.offsets import *
from datetime import datetime, date

def lstm_create_sequences(data, sequence_length):
    sequences = []
    labels = []
    for i in range(len(data) - sequence_length):
        sequences.append(data[i:i + sequence_length])
        labels.append(data[i + sequence_length])
    return np.array(sequences), np.array(labels)


def lstm_create_model(ticker):
    close_data = ticker[['Close']]
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaler_fit=scaler.fit(close_data)
    scaled_data =scaler_fit.transform(close_data)
    sequence_length = 100
    X, y = lstm_create_sequences(scaled_data, sequence_length)
    model = Sequential()
    model.add(LSTM(50, activation="relu", input_shape=(sequence_length, 1)))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    #model.summary()
    split = int(0.9 * len(X))
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    history = model.fit(X_train, y_train, epochs=20, validation_data=(X_test, y_test),verbose=0)
    y_pred = model.predict(X_test, verbose=0)
    y_pred_transform = scaler.inverse_transform(y_pred)
    shape_x=X_test.shape
    prediction_start=len(X_train)+sequence_length
    return model,scaler_fit,X_test,shape_x,prediction_start,y_pred_transform

def lstm_create_file(ticker):
    result = ticker[['Close']].copy()
    result[['Predicted_close', 'Calculated_close', 'Sequential_Prediction']] = np.nan
    result['datetime'] = pd.to_datetime(result.index)
    return result

def lstm_update_file(result,y_pred_transform):
    for i in range(0, len(y_pred_transform)):
        test = y_pred_transform[-i - 1]
        result.loc[result.index[-i - 1], 'Predicted_close'] = test
    return result

def lstm_update_file_after_prediction(result):
    for x in result.index.tolist():
        if (np.isnan(result.loc[x,'Close'])):
            result.loc[x, 'Calculated_close'] = result.loc[x, 'Sequential_Prediction']
        else:
            result.loc[x, 'Calculated_close'] = result.loc[x, 'Close']
    return result

def lstm_add_new_dates(result):
    add_dates = 300
    i = 0
    starting_date = result.index[-1]
    while (i < add_dates):
        orig_date = pd.to_datetime(starting_date)
        new_date = orig_date + BusinessDay()
        new_date_st = new_date.strftime('%Y-%m-%d')
        result.loc[new_date_st, 'datetime'] = pd.to_datetime(new_date_st)
        starting_date = new_date_st
        i = i + 1
    return result

def lstm_upload_data(result,X_test,shape_x,scaler,model,prediction_start):
    i = 0
    new_array = X_test
    list1 = result.index[prediction_start:].to_list()
    while (i < 300):
        new_value = model.predict(new_array, verbose=0)
        temp_flatten = new_array.flatten()
        temp2 = np.append(temp_flatten, new_value[0][0])
        # print(temp2)
        temp3 = np.delete(temp2, 0)
        # print(temp3)
        new_array = temp3.reshape(shape_x[0], shape_x[1],shape_x[2])
        # print(new_value[0][0])
        predict_value = scaler.inverse_transform(new_value)[0][0]
        # print(predict_value)
        update_date = list1[i]
        #print(f"Updated for {update_date} value {predict_value}")
        result.loc[update_date, 'Sequential_Prediction'] = predict_value
        i = i + 1
    return result