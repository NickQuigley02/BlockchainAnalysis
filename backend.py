import requests
from flask import Flask, render_template, request

backend = Flask(__name__)

@backend.route('/')
def index():
    return 'Welcome to the BTC Transaction dashboard!'
    
@backend.route('/transaction', methods=['GET','POST'])
def transaction():
    if request.method == 'POST':
        transaction_id = request.form.get('transaction_id')
        if transaction_id:
            transaction_data = get_transaction_data(transaction_id)
            return render_template('transaction.html', transaction_data=transaction_data)
        else:
            error_message = 'You done messed up with the transaction ID.'
            return render_template('error.html', error_message=error_message)
    
    return render_template('transaction_form.html')
    
def get_transaction_data(transaction_id):
    blockchaincom_url = f'https://blockchain.info/rawtx/{transaction_id}'
    response = requests.get(blockchaincom_url)
    
    if response.status_code == 200:
        print(response.json())
        return(response.json())
    else:
        return None

if __name__ == '__main__':
    backend.run(debug=True)