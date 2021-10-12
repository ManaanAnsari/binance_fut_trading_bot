import pymongo
from indicators import SuperTrend,EMA
from notifier import send_telegram_message
import pandas as pd
import numpy as np 
from order_handler import enter_trade,exit_trade,getMarketPrice
from  global_vars import  db_url
import threading
from notifier import notify_insta


def do_calculations():
    # supper trend config
    period = 14
    multiplier = 3
    # get database
    myclient = pymongo.MongoClient(db_url)
    db = myclient.blockchain_db
    collection = db["BTCUSDT-FUT-15m"]

    # get all the rows
    df = pd.DataFrame(list(collection.find().sort([('machine_time', -1)]).limit(1000)))
    df.sort_values(by='machine_time', ascending=True,inplace=True)
    df.set_index('machine_time',inplace=True)

    # impliment supertrend
    df = SuperTrend(df,int(period),int(multiplier),ohlc=['open', 'high', 'low', 'close'])

    df['up_or_down'] = 0.0
    df['up_or_down'] = np.where(df['ST_'+str(period)+'_'+str(multiplier)] > df['close'], 0, 1)
    # get crossovers
    df['signal'] = df['up_or_down'].diff()
    
    # apply ema
    df = EMA(df, 'close', 'close_ema_200',200)
    # get last row
    row = df.iloc[-1]
    

    if row['signal'] ==1 and row["close"] > row["close_ema_200"]:
        # enter
        send_telegram_message(messages=["buy btc fut"])
        
        try:
            enter_trade()
        except Exception as e:
            send_telegram_message(messages=[str(e)])
            print(e)

        market = getMarketPrice()        
        posting_thread = threading.Thread(target=notify_insta, name="posting_thread",args=(market,'BTC'))
        print('posting_thread started')
        posting_thread.start()
        
    elif row['signal'] == -1:
        # exit
        send_telegram_message(messages=["sell btc fut"])
        exit_trade()
    