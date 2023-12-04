import requests
import http.client
from datetime import datetime
from flask import Flask, render_template, request
from config import CRYPTO_API

'''
This is an OSINT Dashboard project by Nick Quigley for Dr. Dawson's ITMS 448 Cyber Sec Tech
It provides information about BTC transactions.
'''
backend = Flask(__name__)


def timestamp_to_datetime(timestamp): ##this is some bull shit to convert epoch time to date and time.
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

backend.jinja_env.filters['timestamp_to_datetime'] = timestamp_to_datetime   

@backend.route('/') ##basic index page of the site, provides a truly welcoming environment.
def index():
    return 'Welcome to the BTC Transaction dashboard!'
    
@backend.route('/transaction', methods=['GET','POST'])##this is a basic transaction viewer. May make this the main site later but for now, c'est la vie
##also, flask routes are cool as hell, basically a framework to make webpages with whatever code. In this case, defined by the name of the function/one called in the .route()
def transaction():
    ##whis is the basic mechanism of the web page
    if request.method == 'POST': ##keep it to POST requests
        transaction_id = request.form.get('transaction_id')##get the transaction_id from the form at site/transaction
        if transaction_id:
            transaction_data = get_transaction_data(transaction_id)
            return render_template('transaction.html', transaction_data=transaction_data)
        else:
            error_message = 'You done messed up with the transaction ID.'#brief error handling
            return render_template('error.html', error_message=error_message)
    
    return render_template('transaction_form.html')
    
def get_transaction_data(transaction_id):
    ##this gets transaction data from the blockchain.com raw transaction data api
    blockchaincom_url = f'https://blockchain.info/rawtx/{transaction_id}'##retrieves data about a transaction ID based on the hash provided.
    response = requests.get(blockchaincom_url)
    
    if response.status_code == 200: ##assuming all goes well
        transaction_data = response.json()

        ##fetchs the USD value using CoinGecko API
        btc_amount = transaction_data['out'][0]['value'] / 100000000
        usd_value = get_usd_value(btc_amount, transaction_data['time'])

        ##adds the USD value to the transaction data
        transaction_data['usd_value'] = usd_value
        print(transaction_data['usd_value'])
        return(transaction_data)
    else:
        return None
        
def get_usd_value(btc_amount, timestamp):
    ##this function gets the USD dollar value of the transaction based on when the transaction took place. Uses the coingecko price API
    coingecko_url = f'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&date={timestamp}'
    response = requests.get(coingecko_url)
    
    if response.status_code == 200:
        bitcoin_to_usd = response.json()['bitcoin']['usd']
        usd_value = btc_amount * bitcoin_to_usd
        print(f"BTC Amount: {btc_amount}, Bitcoin to USD: {bitcoin_to_usd}, USD Value: {usd_value}")
        return usd_value
    else:
        return None        
        
def get_subsequent_transactions(wallet_address):
    ##this function finds from wallet data -> Transaction data, so we can string together for some amount of depth.
    '''conn = http.client.HTTPSConnection("rest.cryptoapis.io")
    path = f'/blockchain-data/bitcoin/testnet/addresses/{wallet_address}/transactions-by-time-range'
    querystring = "limit=50&offset=0&fromTimestamp=1236238648&toTimestamp=1644417868"

    params = {
        "limit": limit,
        "offset": 0, 
        "fromTimestamp": start_date,
        "toTimestamp": end_date
    }

    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': CRYPTO_API
    }
    
    
    full_path = f"{path}?{querystring}"
    
    
    conn.request("GET", full_path, headers=headers)

    res = conn.getresponse()
    data = res.read()

    print(data.decode("utf-8"))

    response = data.decode("utf-8")'''
    
    blockchair_url = f'https://api.blockchair.com/bitcoin/dashboards/address/{wallet_address}?transaction_details=true&omni=true&limit=10'
    response = requests.get(blockchair_url)
    
    print(response)
    print('TEST1')
    if 1==1:##response.status_code == 200:
        wallet_data = response.json()
        print('TEST2')
        print(wallet_data)
        
        print(wallet_address)
        
        
        
        transactions = wallet_data.get('data', {}).get(wallet_address, {}).get('transactions', []) ##this API gives a list of transactiond made by an account. We're going to go through and only go over ones in the "Accepted date range"
        print(transactions)
        
        ##you'll never guess what this does \/
        filtered_transactions = []
        
        for transaction in transactions:
            transaction_date = transaction['time']
            transaction_details = get_transaction_data(transaction['hash']);
            filtered_transactions.append({
                'transaction_id': transaction['hash'],
                'date': transaction_date,
                'out': transaction_details['out'],
                'usd_value': transaction_details['usd_value'],
                ##'output': transaction_details['output']
                'inputs': transaction_details['inputs']
            })
        print(filtered_transactions)
        return filtered_transactions

    else:
        # Handle the case when the request to CryptoAPIs fails
        print(f"Error: {response.status_code}, {response.text}")
        return []

@backend.route('/trace/<address>')
def trace_address(address):
    subsequent_transactions = get_subsequent_transactions(address)
    
    
    
    if subsequent_transactions:
        return render_template('trace_address.html', address=address, transactions=subsequent_transactions)
    else:
        return render_template('error.html', error_message='No subsequent transactions found for the address'), 404
        
       
if __name__ == '__main__':
    backend.run(debug=True)