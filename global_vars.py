# binance config
API_KEY = "CMFKmo8cNNpDy74syiJ6cbkZ84VZxruVHKJz24q5o2St6Wu560JHWj5FtzpFdnx9"
API_SECRET_KEY = "lIc7yXmqR51Up4XgVPb1F1EpAfzuzw977S0UQnSXckuciFjtDJH83p1I8OjvuEaT"
# database config
# db_url = "mongodb://localhost:27017/"
db_url = "mongodb+srv://admin:admin123@cluster0.byo5q.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
db_name = "blockchain_db"

# order config
target_perc = 0.015 # target is 1.5%
stoploss_perc = 0.01 # sl is 1%
risk_per_trade = 0.1  # (% of amt to risk)
margin = 50  # leverage (50x)
liquidation_distance_perc = 30 # (liquidation price should be 30% away from market price)


# notifier
TELEGRAM_BOT_TOKEN = '1281224512:AAG3F4PHPmi0b1T-L5l4ggXrcwPV42mXA6w'
INSTA_API_ENDPOINT = "https://instacryptobets.herokuapp.com/send_signal/"
