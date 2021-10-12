## what's this?
- stream BTC data using binance websocket
- using **mongo db** as a temp storage for real-time data
- make strategic calculations to derive **buy/sell/hold** signal
- buy/sell binance **BTCUSDT futures** [^long] [^short][^margin]
- notify user on **telegram/insta** about the action 

[^long]: ***long***: when super trend x down close & close is above 200 EMA   
[^short]: ***short***: when super trend x up close & close is below 200 EMA
[^margin]: ***leverage***: default is 50X  (can be changed in global_vars)


### How to use?

`pip install requirements.txt`

***set your env vars in*** `global_vars.py`

`python app.py`







