
from tokens import cmc_token
import requests
from flask import Flask 
from flask import request
from flask import Response
import json
import re

TOKEN = '915049186:AAF2IeXLPJjXqcI9LfMWUbScD_XhlPGCIRw'


app = Flask(__name__)


def write_json(data, filename='response.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_cmc_data(crypto):
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    params = {'symbol': crypto, 'convert': 'USD'}
    headers = {'X-CMC_PRO_API_KEY': cmc_token}
    r = requests.get(url, headers=headers, params=params).json()
    price = r['data'][crypto]['quote']['USD']['price']
    return price

def parse_message(message):
    chat_id = message['message']['chat']['id']
    txt = message['message']['text']    # /btc or /maid

    pattern = r'/[a-zA-Z]{2,4}'
    ticker = re.findall(pattern, txt)   # returns a list [...]
    if ticker:
        symbol = ticker[0][1:].upper()
    else:
        symbol = ''
    
    return chat_id, symbol

def send_message(chat_id, text='blabla'):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    payload = {'chat_id': chat_id, 'text': text}
    r = requests.post(url, json=payload)
    return r


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        msg = request.get_json()
        chat_id, symbol = parse_message(msg)

        if not symbol:
            send_message(chat_id, 'Wrong data')
            return Response('ok', status=200)
        
        price = get_cmc_data(symbol)
        send_message(chat_id, price)
        write_json(msg, 'telegram_request.json')

        # Tells telegram that we recieved the message, if this is not
        # executed then telegram might send us the same message again and again and again 
        return Response('ok', status=200)   
    else:
        return '<h1>CoinMarketCap bot</h1>'

def main():
    print(get_cmc_data('BTC'))
    # https://api.telegram.org/bot915049186:AAF2IeXLPJjXqcI9LfMWUbScD_XhlPGCIRw/getMe
    # https://api.telegram.org/bot915049186:AAF2IeXLPJjXqcI9LfMWUbScD_XhlPGCIRw/setWebhook?url=https://mille.serveo.net/

if __name__ == '__main__':
    # main()
    app.run(debug=True)
