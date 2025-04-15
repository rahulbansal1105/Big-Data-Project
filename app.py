import streamlit as st
import pandas as pd
import os
from datetime import timedelta,datetime
import time
aws_flag=False
if aws_flag:
    pass
else:
    current_directory = os.path.dirname(__file__)

read_file="Scripts_run.csv"
bond_file="Bond_data.csv"



def get_price(df,date,column):
    price=pd.Series()
    #print(len(price))
    while(len(price)==0):
       #print("In nested none")
       price=get_price2(df,date,column)
       new_date=pd.to_datetime(date)+ timedelta(days=1)
       date=new_date.strftime('%Y-%m-%d')
    return price.values[0]
def get_price2(df,date,column):
    price=df.loc[df['datetime']==date,column]
    return price


#detail=pd.read_excel(os.path.join(current_directory,read_file),"Nifty50")
filepath=os.path.join(current_directory,read_file)
detail=pd.read_csv(filepath)
#bond=pd.read_excel(os.path.join(current_directory,bond_file))
filepath=os.path.join(current_directory,bond_file)
bond=pd.read_csv(filepath,parse_dates=["Date"])

listofticker=detail.loc[detail['Model_created']=='Yes','Symbol'].to_list()
listofmodels=['LSTM','Placeholder1', 'Placeholder2']
st.title('Stock price Prediction')

ticker=st.selectbox("Select stock from Nifty 50",listofticker)
model=st.selectbox("Select Model Type",listofmodels)
#ticker='HDFCBANK.NS'
max_date= datetime(2025,4,4)
purchase_date= st.date_input("Purchase Date of " + ticker,max_value=max_date)
#purchase_date='2025/03/03'
purchase_date_dt=pd.to_datetime(purchase_date)
purchase_date_str=purchase_date_dt.strftime('%Y-%m-%d')
Quantity= st.number_input("Quantity of stock",min_value=1, max_value=10000,value=1,step=1)


## calulation details for prediction file"
if model =='LSTM':
    predicted_folder='LSTM_Prediction'
else:
    pass

filepath=os.path.join(current_directory,predicted_folder,ticker+".csv")
predicted_file=pd.read_csv(filepath)
purchase_price=get_price(predicted_file,purchase_date_str,"Calculated_close")
filepath=os.path.join(current_directory,predicted_folder,"HDFCBANK.NS.csv")
ti_c = os.path.getctime(filepath)

x=pd.to_datetime(time.ctime(ti_c))

last_date_str=x.strftime('%Y-%m-%d')
last_price=get_price(predicted_file,last_date_str,"Calculated_close")
date10=pd.to_datetime(last_date_str)+ timedelta(days=10)
date10_str=date10.strftime('%Y-%m-%d')
date20=pd.to_datetime(last_date_str)+ timedelta(days=20)
date20_str=date20.strftime('%Y-%m-%d')
date30=pd.to_datetime(last_date_str)+ timedelta(days=30)
date30_str=date30.strftime('%Y-%m-%d')
price_after_10_days=get_price(predicted_file,date10_str,"Calculated_close")
price_after_20_days=get_price(predicted_file,date20_str,"Calculated_close")
price_after_30_days=get_price(predicted_file,date30_str,"Calculated_close")
###

Amount_invested= Quantity* purchase_price
Total_value_till_date= last_price*Quantity
Total_value_after_10_days=price_after_10_days*Quantity
Total_value_after_20_days=price_after_20_days*Quantity
Total_value_after_30_days=price_after_30_days*Quantity

## calcuation of bond data
rate= bond.loc[bond['Date']>=purchase_date_str,'Price'].mean()
last_price_dt=pd.to_datetime(last_date_str)
date_diff=last_price_dt-purchase_date_dt
n=date_diff.days/365
Bond_value_till_date = Amount_invested* ( 1 + rate/100)**n


#######




st.write(f"Closing price on purchase date  **{int(purchase_price)}**")
st.write(f"Total amount invested **{int(Amount_invested)}**")
st.write(f"Price on last date **{last_date_str}** is **{int(last_price)}**")
st.write(f"Total amount value till date **{int(Total_value_till_date)}**")
st.write(f"Bond would have return amount **{int(Bond_value_till_date)}**")
st.write(f"**Predicton for next 30 days**")
st.write(f"Prediction return value after 10 days **{int(Total_value_after_10_days)}**")
st.write(f"Prediction return value after 20 days **{int(Total_value_after_20_days)}**")
st.write(f"Prediction return value after 30 days **{int(Total_value_after_30_days)}**")