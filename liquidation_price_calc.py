# to get approx liquidation price
maint_lookup_table = [
    (   50000,  0.4,       0),
    (  250000,  0.5,      50),
    ( 1000000,  1.0,    1300),
    ( 5000000,  2.5,   16300),
    (10000000,  5.0,  141300),
    (20000000, 10.0,  641300),
    (35000000, 12.5, 1141300),
    (50000000, 15.0, 2016300),
    (  1e1000, 25.0, 7016300),
]

def lookup_maint(pos):
    pct,amt = [(mr,ma) for p,mr,ma in maint_lookup_table if pos<p][0]
    return pct/100, amt


def binance_btc_liq_balance(wallet_balance, contract_qty, entry_price):
    maint_margin_rate,maint_amount = lookup_maint(wallet_balance)
    liq_price = (wallet_balance + maint_amount - contract_qty*entry_price) / (abs(contract_qty) * (maint_margin_rate - (1 if contract_qty>=0 else -1)))
    return round(liq_price, 2)

