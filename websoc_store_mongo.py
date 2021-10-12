import logging
from binance_f import SubscriptionClient
from binance_f.constant.test import *
from binance_f.model import *
from binance_f.exception.binanceapiexception import BinanceApiException
from binance_f.base.printobject import *

# for storing in database and calculations 
import pymongo
import datetime
import ast
import threading
from calculations import do_calculations
import time
from global_vars import  API_KEY,API_SECRET_KEY,db_url, db_name
from notifier import  send_telegram_message


# create and authenticate object for websocet stream
sub_client = SubscriptionClient(api_key=API_KEY, secret_key=API_SECRET_KEY)

# get our blockchain db
myclient = pymongo.MongoClient(db_url)
blockchain_db = myclient[db_name]

# the core logic of what we 'll be doing with realtime data 
def callback(data_type: 'SubscribeMessageType', event: 'any'):
    if data_type == SubscribeMessageType.RESPONSE:
        print("Event ID: ", event)
    elif  data_type == SubscribeMessageType.PAYLOAD:
        # for safety just catch any possibl err
        try:
            # convert stream object to dict
            data = event.data.__dict__
            # print(data)
            # if candl closed
            if data.get('isClosed',None):
                # just for our reference add machine time
                data["machine_time"] = datetime.datetime.now()
                # print(data)
                # save this data in mongo
                if data.get("symbol",None) == "BTCUSDT":
                    collection_name = blockchain_db["BTCUSDT-FUT-15m"]
                    collection_name.insert_one(data)
                    # todo: calculations and order management async
                    do_calculations()

        except Exception as e:
            send_telegram_message(messages=[str(e)])
            print(e)
            print("Unknown Data:")
        # PrintBasic.print_obj(event.data)
        # sub_client.unsubscribe_all()
    else:
        print("Unknown Data:")


def error(e: 'BinanceApiException'):
    print(e.error_code + e.error_message)

# start subscribtion
sub_client.subscribe_candlestick_event("btcusdt", CandlestickInterval.MIN15, callback, error)
