import requests 
import json
from global_vars import TELEGRAM_BOT_TOKEN, INSTA_API_ENDPOINT


def send_telegram_message(chat_ids=[662144469],messages=[]):
    if TELEGRAM_BOT_TOKEN:
        url = 'https://api.telegram.org/bot'+TELEGRAM_BOT_TOKEN+'/sendMessage' 
        if messages:
            for message in messages:
                for chat_id in chat_ids:
                    payload = {'chat_id' : chat_id,'text' : message}
                    requests.post(url,json=payload)
        return True
    print("TELEGRAM_BOT_TOKEN not set!")


def notify_insta(market,BTCETH='BTC'):
    if INSTA_API_ENDPOINT:
        try:
            market = int(market)
            if market and BTCETH:
                # data to be sent to api
                data = {
                            "BTCETH" :BTCETH,
                            "market": market
                
                        }
                # sending post request and saving response as response object
                r = requests.post(url = INSTA_API_ENDPOINT, data = json.dumps(data))
                print(r.text)
                send_telegram_message(messages=["notify_insta",str(r.text)])
                return True

        except Exception as e:
            print(e)
            send_telegram_message(messages=["error in notify_insta ",str(e)])
        return True
    print("INSTA_API_ENDPOINT is not set!")

