from binance_f import RequestClient
from binance_f.constant.test import *
from binance_f.base.printobject import *
from binance_f.model.constant import *
from liquidation_price_calc import binance_btc_liq_balance
from notifier import send_telegram_message
from global_vars import  *


# create object
request_client = RequestClient(api_key=API_KEY, secret_key=API_SECRET_KEY)


def getCurrentPossition():
    # what amount of btc usdt we still hold
    result = request_client.get_position_v2()
    for r in result:
        if r.symbol == 'BTCUSDT':
            return float(r.positionAmt)
    return None


def getBalance():
    # whats your walet balance
    result = request_client.get_balance_v2()
    for r in result:
        if r.asset == 'USDT':
            return r.availableBalance
    return None


def getMarketPrice():
    # current market price of btc usdt fut
    result = request_client.get_mark_price(symbol="BTCUSDT")
    return result.markPrice


def getQuantityForNewTrade():
    # the minimum  qty allowed
    minimum_quantity = 0.001
    # whats the balane
    balance = getBalance()
    # whats the current market price
    marketPrice = getMarketPrice()
    # risk 15% of your balance
    amount_to_risk = balance*risk_per_trade
    # what qty can you actually get 
    max_qty = round(max(round(((amount_to_risk*margin)/marketPrice),3)- 0.001,minimum_quantity),3)
    qty_to_trade = max_qty
    # a temp variable 
    previous_qty = 0
    qtys = []
    # if its minimum qty then ignore
    while qty_to_trade > minimum_quantity  and qty_to_trade >0 and qty_to_trade<=max_qty:
        qty_to_trade = round(qty_to_trade,3)
        # get liquidation price
        liquidationPrice = binance_btc_liq_balance(balance,qty_to_trade,marketPrice)
        liq_perc = round((marketPrice - liquidationPrice)/marketPrice,2)*100
        # if its 20 thats all we need
        if liq_perc == liquidation_distance_perc:
            break
        
        elif liq_perc < liquidation_distance_perc:
            qty_to_trade -=0.001
        else:
            qty_to_trade +=0.001
        # if we are circling back break it
        if previous_qty == qty_to_trade:
            break
        else:
            previous_qty = qty_to_trade
        
        qtys.append(qty_to_trade)
        if qtys.count(qty_to_trade) >3:
            break
    
    # just evaluating conditions once again
    if qty_to_trade > max_qty:
        qty_to_trade = max_qty
    
    if qty_to_trade < 0:
        qty_to_trade = 0
    
    if qty_to_trade < minimum_quantity:
        qty_to_trade = 0

    if qty_to_trade: 
        # double check if you can afford to trade this qty
        if (balance >=( (qty_to_trade*marketPrice)/margin)):
            return qty_to_trade
        else:
            # cant afford
            return 0
    return 0
    

def enter_trade():
    # get current position
    current_position = getCurrentPossition()
    if current_position:
        if current_position < 0:
            # previously sold
            # square this off
            buy(abs(current_position))
        else:
            # already in buy position so ignore this
            return
    # if not in the market
    # get the quantity to trade 
    quantity = getQuantityForNewTrade()
    quantity = round(quantity,3)
    # max precission allowed is 0.008 will figure out a way to bypass this 
    if quantity:
        # buy it
        buy(quantity)
        print('buying futures')
    else:
        print("quantity is "+str(quantity))


def exit_trade():
    # get current position
    current_position = getCurrentPossition()
    if current_position:
        if current_position > 0:
            # if in the long trade
            sell(abs(current_position))
        else:
            # if already in short position then ignore this
            return
    # if not in the market 
    # get quantity to trade
    quantity = getQuantityForNewTrade()
    quantity = round(quantity,3)
    if quantity:
        # sell it
        sell(quantity)
        print('selling futures')
    else:
        print("quantity is "+str(quantity))


def buy(quantity):
    # simple buy 
    # max 
    max_qty_allowed = 0.008
    mark_p = getMarketPrice()
    target = int(mark_p + mark_p*target_perc)
    stoploss = int(mark_p - mark_p*stoploss_perc)
    add_tpsl = None
    # close open orders
    result = request_client.cancel_all_orders(symbol="BTCUSDT")
    try:
        while quantity > max_qty_allowed:
            quantity = round(quantity,3)
            result = request_client.post_order(symbol="BTCUSDT", side=OrderSide.BUY, quantity = max_qty_allowed,ordertype=OrderType.MARKET)
            send_telegram_message(messages=["buying btc fut of "+str(max_qty_allowed)])
            quantity -= max_qty_allowed
            add_tpsl = True
        if quantity:
            quantity = round(quantity,3)
            result = request_client.post_order(symbol="BTCUSDT", side=OrderSide.BUY, quantity = quantity,ordertype=OrderType.MARKET)
            send_telegram_message(messages=["buying btc fut of "+str(quantity)])
            add_tpsl = True
    except Exception as e:
        print(e)
        send_telegram_message(messages=[str(e)])
        
    if add_tpsl:
        # stoploss
        result = request_client.post_order(symbol="BTCUSDT", side=OrderSide.SELL, ordertype=OrderType.STOP_MARKET, stopPrice=stoploss, closePosition=True)
        # target
        result = request_client.post_order(symbol="BTCUSDT", side=OrderSide.SELL, ordertype=OrderType.TAKE_PROFIT_MARKET, stopPrice=target, closePosition=True)
        # notify
        send_telegram_message(messages=["btc tp at "+str(target)+" sl at "+str(stoploss)+" market at "+str(mark_p)])


def sell(quantity):
    # simple sell
    max_qty_allowed = 0.008
    # close open orders
    result = request_client.cancel_all_orders(symbol="BTCUSDT")

    while quantity > max_qty_allowed:
        quantity = round(quantity,3)
        result = request_client.post_order(symbol="BTCUSDT", side=OrderSide.SELL, quantity = max_qty_allowed,ordertype=OrderType.MARKET)
        send_telegram_message(messages=["selling btc fut of "+str(max_qty_allowed)])
        quantity -= max_qty_allowed
    if quantity:
        quantity = round(quantity,3)
        result = request_client.post_order(symbol="BTCUSDT", side=OrderSide.SELL, quantity = quantity,ordertype=OrderType.MARKET)
        send_telegram_message(messages=["selling btc fut of "+str(quantity)])


