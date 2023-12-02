import requests
from datetime import datetime
from flask import Flask, render_template, request
'''
This is an OSINT Dashboard project by Nick Quigley for Dr. Dawson's ITMS 448 Cyber Sec Tech
It provides information about BTC transactions.
'''
backend = Flask(__name__)


def timestamp_to_datetime(timestamp): #this is some bull shit to convert epoch time to date and time.
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

backend.jinja_env.filters['timestamp_to_datetime'] = timestamp_to_datetime   

@backend.route('/') #basic index page of the site, provides a truly welcoming environment.
def index():
    return 'Welcome to the BTC Transaction dashboard!'
    
@backend.route('/transaction', methods=['GET','POST'])#this is a basic transaction viewer. May make this the main site later but for now, c'est la vie
def transaction():
    if request.method == 'POST': ##keep it to POST requests
        transaction_id = request.form.get('transaction_id')#get the transaction_id from the form at site/transaction
        if transaction_id:
            transaction_data = get_transaction_data(transaction_id)
            return render_template('transaction.html', transaction_data=transaction_data)
        else:
            error_message = 'You done messed up with the transaction ID.'#brief error handling
            return render_template('error.html', error_message=error_message)
    
    return render_template('transaction_form.html')
    
def get_transaction_data(transaction_id):
    blockchaincom_url = f'https://blockchain.info/rawtx/{transaction_id}'##retrieves data about a transaction ID based on the hash provided.
    response = requests.get(blockchaincom_url)
    
    if response.status_code == 200: ##assuming all goes well
        transaction_data = response.json()

        #fetchs the USD value using CoinGecko API
        btc_amount = transaction_data['out'][0]['value'] / 100000000
        usd_value = get_usd_value(btc_amount, transaction_data['time'])

        #adds the USD value to the transaction data
        transaction_data['usd_value'] = usd_value
        print(transaction_data['usd_value'])
        return(transaction_data)
    else:
        return None
        
def get_usd_value(btc_amount, timestamp):
    coingecko_url = f'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&date={timestamp}'
    response = requests.get(coingecko_url)
    
    if response.status_code == 200:
        bitcoin_to_usd = response.json()['bitcoin']['usd']
        usd_value = btc_amount * bitcoin_to_usd
        print(f"BTC Amount: {btc_amount}, Bitcoin to USD: {bitcoin_to_usd}, USD Value: {usd_value}")
        return usd_value
    else:
        return None        

if __name__ == '__main__':
    backend.run(debug=True)