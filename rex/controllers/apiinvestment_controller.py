from bson.json_util import dumps
from flask import Blueprint, jsonify,session, request, redirect, url_for, render_template, json, flash
from flask.ext.login import current_user, login_required
from rex import db, lm
from rex.models import user_model, deposit_model, history_model, invoice_model
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from datetime import datetime
from datetime import datetime, date, timedelta
from time import gmtime, strftime
import time
import json
import os
from validate_email import validate_email
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from bson import ObjectId, json_util
import codecs
from random import randint
from hashlib import sha256
import string
import random
import urllib
import urllib2
import base64
import onetimepass
import sys
import time
import requests
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
sys.setrecursionlimit(10000)
digits58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

from rex.coinpayments import CoinPaymentsAPI
from rex.config import Config

ApiCoinpayment = CoinPaymentsAPI(public_key=Config().public_key,
                          private_key=Config().private_key)

__author__ = 'asdasd'

apiinvestment_ctrl = Blueprint('investment', __name__, static_folder='static', template_folder='templates')
def check_password(pw_hash, password):
        return check_password_hash(pw_hash, password)
@apiinvestment_ctrl.route('/testinvest', methods=['GET', 'POST'])
def testinvest():
    Update_level_all_user()
    time.sleep( 5 )
    caculator_profitDaily()

    return json.dumps({
        'status': 'complete' 
        
    })

@apiinvestment_ctrl.route('/active-package', methods=['GET', 'POST'])
def active_package():
    dataDict = json.loads(request.data)
    customer_id = dataDict['customer_id']
    currency = dataDict['currency']
    amount = dataDict['amount']
    password_transaction = dataDict['password_transaction']

    user = db.User.find_one({'customer_id': customer_id})

    if check_password(user['password_transaction'], password_transaction) == True:

        if user is not None:
            ticker = db.tickers.find_one({})
            if currency == 'BTC': 
                price_atlcoin = ticker['btc_usd']
                string_query = 'balance.bitcoin.available'
                val_balance = user['balance']['bitcoin']['available']
            if currency == 'ETH':
                price_atlcoin = ticker['eth_usd']
                string_query = 'balance.ethereum.available'
                val_balance = user['balance']['ethereum']['available']
            if currency == 'LTC':
                price_atlcoin = ticker['ltc_usd']
                string_query = 'balance.litecoin.available'
                val_balance = user['balance']['litecoin']['available']
            if currency == 'XRP':
                price_atlcoin = ticker['xrp_usd']
                string_query = 'balance.ripple.available'
                val_balance = user['balance']['ripple']['available']
            if currency == 'USDT':
                price_atlcoin = ticker['usdt_usd']
                string_query = 'balance.tether.available'
                val_balance = user['balance']['tether']['available']
            if currency == 'DASH':
                price_atlcoin = ticker['dash_usd']
                string_query = 'balance.dash.available'
                val_balance = user['balance']['dash']['available']
            if currency == 'EOS':
                price_atlcoin = ticker['eso_usd']
                string_query = 'balance.eos.available'
                val_balance = user['balance']['eos']['available']
            if currency == 'ASIC':
                price_atlcoin = ticker['coin_usd']
                string_query = 'balance.coin.available'
                val_balance = user['balance']['coin']['available']

            if float(val_balance) >= float(amount)*100000000:
                amount_usd = float(amount)*float(price_atlcoin)
                if float(amount_usd) >= 500:
                    new_balance_sub = round((float(val_balance) - float(amount)*100000000),8)

                    new_invest_ss = float(user['investment'])+float(amount_usd)

                    db.users.update({ "customer_id" : customer_id }, { '$set': { string_query: float(new_balance_sub),'investment' : new_invest_ss} })
                    
                    #save lich su
                    data_investment = {
                        'uid' : customer_id,
                        'user_id': str(user['_id']),
                        'username' : user['email'],
                        'amount_usd' : float(amount_usd),
                        'package': round(float(amount),8),
                        'status' : 1,
                        'date_added' : datetime.utcnow(),
                        'amount_frofit' : 0,
                        'coin_amount' : 0,
                        'total_income' : '',
                        'status_income' : 0,
                        'date_income' : '',
                        'date_profit' : datetime.utcnow(), #+ timedelta(days=3)
                        'currency' : currency
                    }
                    db.investments.insert(data_investment)

                    #save dialing
                    data_dialing = {
                        'customer_id' : customer_id,
                        'username' : user['email'],
                        'package': round(float(amount),8),
                        'status' : 0,
                        'date_added' : datetime.utcnow(),
                        'amount_coin' : 0,
                        'currency' : currency
                    }
                    db.dialings.insert(data_dialing)


                    FnRefferalProgram(customer_id, amount, currency)

                    TotalnodeAmount(customer_id, amount,currency)

                    return json.dumps({
                        'status': 'complete', 
                        'message': 'Ai trade successfully' 
                    })
                else:
                    return json.dumps({
                        'status': 'error',
                        'message': 'The minimum amount of ai-trade is '+str(round(500/float(price_atlcoin),8))+' '+currency 
                    })
            else:
                return json.dumps({
                    'status': 'error',
                    'message': 'Account balance is not enough to Ai-trade' 
                })

        else:
          return json.dumps({
              'status': 'error'
          })
    else:
        return json.dumps({
            'status': 'error', 
            'message': 'Wrong password transaction. Please try again' 
        })
    


@apiinvestment_ctrl.route('/disable-package', methods=['GET', 'POST'])
def disable_package():

    dataDict = json.loads(request.data)
    customer_id = dataDict['customer_id']
    currency = dataDict['currency']
    
    val_add_balance = 0

    investment = db.investments.find({'$and' : [{'uid': customer_id},{'currency': currency},{'status' : 1}]})
    for item in investment:
        val_add_balance += item['package']*0.89*100000000
        db.investments.update({ "_id" : ObjectId(item['_id']) }, { '$set': { 'status': 0} })

    user = db.User.find_one({'customer_id': customer_id})

    if currency == 'BTC': 
        string_query = 'balance.bitcoin.available'
        val_balance = user['balance']['bitcoin']['available']
    if currency == 'ETH':
        string_query = 'balance.ethereum.available'
        val_balance = user['balance']['ethereum']['available']
    if currency == 'LTC':
        string_query = 'balance.litecoin.available'
        val_balance = user['balance']['litecoin']['available']
    if currency == 'XRP':
        string_query = 'balance.ripple.available'
        val_balance = user['balance']['ripple']['available']
    if currency == 'USDT':
        string_query = 'balance.tether.available'
        val_balance = user['balance']['tether']['available']
    if currency == 'DASH':
        string_query = 'balance.dash.available'
        val_balance = user['balance']['dash']['available']
    if currency == 'EOS':
        string_query = 'balance.eos.available'
        val_balance = user['balance']['eos']['available']
    if currency == 'ASIC':
        string_query = 'balance.coin.available'
        val_balance = user['balance']['coin']['available']

    new_balance_add = float(val_balance) + float(val_add_balance)

              
    db.users.update({ "customer_id" : customer_id }, { '$set': { string_query: float(new_balance_add) ,'investment' : 0 } })


    customer = db.User.find_one({'customer_id': customer_id})

    investments = db.investments.find({'$and' : [{'uid': customer_id},{'status' : 1}]})
    investment_usd = 0
    for items in investments:
        investment_usd += float(items['amount_usd'])
    if  float(investment_usd) > 0:
        db.users.update({ "customer_id" : customer_id }, { '$set': { 'investment' : investment_usd } })

    return json.dumps({
        'status': 'complete', 
        'message': 'Disable Ai trade successfully' 
    })
@apiinvestment_ctrl.route('/get-history', methods=['GET', 'POST'])
def get_historys_investment():

    dataDict = json.loads(request.data)
    customer_id = dataDict['customer_id']
    start = dataDict['start']
    limit = dataDict['limit']
    investment = db.investments.find({'uid': customer_id}).sort([("date_added", -1)]).limit(limit).skip(start)

    
    array = []
    for item in investment:
      array.append({
        "username" : item['username'],
        "package" : item['package'],
        "currency" : item['currency'],
        "status" : item['status'],
        "amount_usd" : item['amount_usd'],
        "date_added" : (item['date_added']).strftime('%H:%M %d-%m-%Y')
      })
    return json.dumps(array)

@apiinvestment_ctrl.route('/get-active-invest', methods=['GET', 'POST'])
def get_active_investment():

    dataDict = json.loads(request.data)
    customer_id = dataDict['customer_id']
   
    investment = db.investments.find({'$and' :[{'uid': customer_id},{'status' : 1}]})

    
    array = []
    for item in investment:
      array.append({
        "package" : item['package'],
        "currency" : item['currency'],
        "amount_usd" : item['amount_usd'],
        "date_added" : (item['date_added']).strftime('%H:%M %d-%m-%Y')
      })
    return json.dumps(array)

@apiinvestment_ctrl.route('/get-active-invest-currency', methods=['GET', 'POST'])
def get_active_investment_currency():

    dataDict = json.loads(request.data)
    customer_id = dataDict['customer_id']
    currency = dataDict['currency']
    investment = db.investments.find({'$and' :[{'uid': customer_id},{'status' : 1},{'currency' : currency}]})

    
    amount_invest = 0
    for item in investment:
        amount_invest += float(item['package'])
    return json.dumps({
        'status': 'complete', 
        'amount': amount_invest 
    })

@apiinvestment_ctrl.route('/submit-payment', methods=['GET', 'POST'])
def submit_payment():
    dataDict = json.loads(request.data)
    customer_id = dataDict['customer_id']
    address = dataDict['address']
    currency = dataDict['currency']
    amount = dataDict['amount']
    password_transaction = dataDict['password_transaction']

    user = db.User.find_one({'customer_id': customer_id})
    if int(user['security']['email']['status']) == 1:
        if check_password(user['password_transaction'], password_transaction) == True:

            if user is not None:
                ticker = db.tickers.find_one({})
                if currency == 'BTC': 
                    price_atlcoin = ticker['btc_usd']
                    string_query = 'balance.bitcoin.available'
                    string_query_address = 'balance.bitcoin.cryptoaddress'
                    val_balance = user['balance']['bitcoin']['available']
                if currency == 'ETH':
                    price_atlcoin = ticker['eth_usd']
                    string_query = 'balance.ethereum.available'
                    val_balance = user['balance']['ethereum']['available']
                    string_query_address = 'balance.ethereum.cryptoaddress'
                if currency == 'LTC':
                    price_atlcoin = ticker['ltc_usd']
                    string_query = 'balance.litecoin.available'
                    val_balance = user['balance']['litecoin']['available']
                    string_query_address = 'balance.litecoin.cryptoaddress'
                if currency == 'XRP':
                    price_atlcoin = ticker['xrp_usd']
                    string_query = 'balance.ripple.available'
                    val_balance = user['balance']['ripple']['available']
                    string_query_address = 'balance.ripple.cryptoaddress'
                if currency == 'USDT':
                    price_atlcoin = ticker['usdt_usd']
                    string_query = 'balance.tether.available'
                    val_balance = user['balance']['tether']['available']
                    string_query_address = 'balance.tether.cryptoaddress'
                if currency == 'DASH':
                    price_atlcoin = ticker['dash_usd']
                    string_query = 'balance.dash.available'
                    val_balance = user['balance']['dash']['available']
                    string_query_address = 'balance.dash.cryptoaddress'
                if currency == 'EOS':
                    price_atlcoin = ticker['eso_usd']
                    string_query = 'balance.eos.available'
                    val_balance = user['balance']['eos']['available']
                    string_query_address = 'balance.eos.cryptoaddress'
                if currency == 'ASIC':
                    price_atlcoin = ticker['coin_usd']
                    string_query = 'balance.coin.available'
                    val_balance = user['balance']['coin']['available']
                    string_query_address = 'balance.coin.cryptoaddress'

                if float(val_balance) >= float(amount)*100000000:
                        amount_usd = float(amount)*float(price_atlcoin)

                        user_receve = db.User.find_one({string_query_address: address})
                        
                        if user_receve is not None:


                            new_balance_sub = round((float(val_balance) - float(amount)*100000000),8)
                          
                            db.users.update({ "customer_id" : customer_id }, { '$set': { string_query: float(new_balance_sub)} })
                            
                            if currency == 'BTC': 
                                price_atlcoin = ticker['btc_usd']
                                string_query = 'balance.bitcoin.available'
                                val_balance_receve = user_receve['balance']['bitcoin']['available']
                            if currency == 'ETH':
                                price_atlcoin = ticker['eth_usd']
                                string_query = 'balance.ethereum.available'
                                val_balance_receve = user_receve['balance']['ethereum']['available']
                            if currency == 'LTC':
                                price_atlcoin = ticker['ltc_usd']
                                string_query = 'balance.litecoin.available'
                                val_balance_receve = user_receve['balance']['litecoin']['available']
                            if currency == 'XRP':
                                price_atlcoin = ticker['xrp_usd']
                                string_query = 'balance.ripple.available'
                                val_balance_receve = user_receve['balance']['ripple']['available']
                            if currency == 'USDT':
                                price_atlcoin = ticker['usdt_usd']
                                string_query = 'balance.tether.available'
                                val_balance_receve = user_receve['balance']['tether']['available']
                            if currency == 'DASH':
                                price_atlcoin = ticker['dash_usd']
                                string_query = 'balance.dash.available'
                                val_balance_receve = user_receve['balance']['dash']['available']
                            if currency == 'EOS':
                                price_atlcoin = ticker['eso_usd']
                                string_query = 'balance.eos.available'
                                val_balance_receve = user_receve['balance']['eos']['available']
                            if currency == 'ASIC':
                                price_atlcoin = ticker['coin_usd']
                                string_query = 'balance.coin.available'
                                val_balance_receve = user_receve['balance']['coin']['available']

                            new_balance_add = round((float(val_balance_receve) + float(amount)*100000000),8)
                          
                            db.users.update({ "customer_id" : user_receve['customer_id'] }, { '$set': { string_query: float(new_balance_add)} })
                            
                            #save lich su
                            data_payment_sub = {
                                'uid' : customer_id,
                                'user_id': str(user['_id']),
                                'username' : user['email'],
                                'amount_usd' : float(amount_usd),
                                'amount' : amount,
                                'status' : 1,
                                'date_added' : datetime.utcnow(),
                                'address' : address,
                                'currency' : currency,
                                'types' : 'send'
                            }
                            db.payments.insert(data_payment_sub)

                            data_payment_add = {
                                'uid' : user_receve['customer_id'],
                                'user_id': str(user_receve['_id']),
                                'username' : user_receve['email'],
                                'amount_usd' : float(amount_usd),
                                'amount' : amount,
                                'status' : 1,
                                'date_added' : datetime.utcnow(),
                                'address' : address,
                                'currency' : currency,
                                'types' : 'receive'
                            }
                            db.payments.insert(data_payment_add)

                            
                            return json.dumps({
                                'status': 'complete', 
                                'message': 'Payment successfully' 
                            })
                        else:
                            return json.dumps({
                                'status': 'error',
                                'message': 'Awrong payment information' 
                            })
                   
                else:
                    return json.dumps({
                        'status': 'error',
                        'message': 'Account balance is not enough to payment' 
                    })

            else:
              return json.dumps({
                  'status': 'error'
              })
        else:
            return json.dumps({
                'status': 'error', 
                'message': 'Wrong password transaction. Please try again' 
            })
    else:
        return json.dumps({
            'status': 'error', 
            'message': 'Your account has not been verify.' 
        })

@apiinvestment_ctrl.route('/get-history-payment', methods=['GET', 'POST'])
def get_history_payment():

    dataDict = json.loads(request.data)
    customer_id = dataDict['customer_id']
    start = dataDict['start']
    limit = dataDict['limit']
    investment = db.payments.find({'uid': customer_id}).sort([("date_added", -1)]).limit(limit).skip(start)

    
    array = []
    for item in investment:
      array.append({

        "username" : item['username'],
        "amount" : item['amount'],
        "currency" : item['currency'],
        "status" : item['status'],
        "address" : item['address'],
        "types" : item['types'],
        "date_added" : (item['date_added']).strftime('%H:%M %d-%m-%Y')
      })
    return json.dumps(array)

def FnRefferalProgram(customer_id, amount_invest, currency):
    customers = db.users.find_one({"customer_id" : customer_id })
    if customers['p_node'] != '':
        customers_pnode = db.users.find_one({"customer_id" : customers['p_node'] })

        if float(customers_pnode['investment'] > 0):
            ticker = db.tickers.find_one({})

            if currency == 'BTC': 
                price_atlcoin = ticker['btc_usd']
                string_query = 'balance.bitcoin.available'
                val_balance = customers_pnode['balance']['bitcoin']['available']
            if currency == 'ETH':
                price_atlcoin = ticker['eth_usd']
                string_query = 'balance.ethereum.available'
                val_balance = customers_pnode['balance']['ethereum']['available']
            if currency == 'LTC':
                price_atlcoin = ticker['ltc_usd']
                string_query = 'balance.litecoin.available'
                val_balance = customers_pnode['balance']['litecoin']['available']
            if currency == 'XRP':
                price_atlcoin = ticker['xrp_usd']
                string_query = 'balance.ripple.available'
                val_balance = customers_pnode['balance']['ripple']['available']
            if currency == 'USDT':
                price_atlcoin = ticker['usdt_usd']
                string_query = 'balance.tether.available'
                val_balance = customers_pnode['balance']['tether']['available']
            if currency == 'DASH':
                price_atlcoin = ticker['dash_usd']
                string_query = 'balance.dash.available'
                val_balance = customers_pnode['balance']['dash']['available']
            if currency == 'EOS':
                price_atlcoin = ticker['eso_usd']
                string_query = 'balance.eos.available'
                val_balance = customers_pnode['balance']['eos']['available']
            if currency == 'ASIC':
                price_atlcoin = ticker['coin_usd']
                string_query = 'balance.coin.available'
                val_balance = customers_pnode['balance']['coin']['available']

           
            
            commission = float(price_atlcoin)*float(amount_invest)*0.03

            r_wallet = float(customers_pnode['r_wallet'])
            new_r_wallet = float(r_wallet) + float(commission)
            new_r_wallet = float(new_r_wallet)

            total_earn = float(customers_pnode['total_earn'])
            new_total_earn = float(total_earn) + float(commission)
            new_total_earn = float(new_total_earn)

            balance_wallet = float(val_balance)
            new_balance_wallet = float(balance_wallet) + (float(amount_invest)*0.03*100000000)
            new_balance_wallet = round(float(new_balance_wallet),8)

            db.users.update({ "_id" : ObjectId(customers_pnode['_id']) }, { '$set': {string_query : new_balance_wallet,'total_earn': new_total_earn, 'r_wallet' :new_r_wallet } })
            
            detail = str(customers['email']) + ' Ai-trade '+ str(amount_invest) + ' ' + str(currency)
            SaveHistory(customers_pnode['customer_id'],customers_pnode['email'],detail, float(amount_invest)*0.03, currency, 'Direct commission')
   
    return True

def caculator_profitDaily():
    
    get_percent = db.profits.find_one({});
    percent = get_percent['percent']

    get_invest = db.investments.find({ "status": 1});
    ticker = db.tickers.find_one({})
    for x in get_invest:
        
        customer = db.users.find_one({'customer_id': x['uid']})
        if customer is not None:


            if x['currency'] == 'BTC': 
                price_atlcoin = ticker['btc_usd']
                string_query = 'balance.bitcoin.available'
                val_balance = customer['balance']['bitcoin']['available']
            if x['currency'] == 'ETH':
                price_atlcoin = ticker['eth_usd']
                string_query = 'balance.ethereum.available'
                val_balance = customer['balance']['ethereum']['available']
            if x['currency'] == 'LTC':
                price_atlcoin = ticker['ltc_usd']
                string_query = 'balance.litecoin.available'
                val_balance = customer['balance']['litecoin']['available']
            if x['currency'] == 'XRP':
                price_atlcoin = ticker['xrp_usd']
                string_query = 'balance.ripple.available'
                val_balance = customer['balance']['ripple']['available']
            if x['currency'] == 'USDT':
                price_atlcoin = ticker['usdt_usd']
                string_query = 'balance.tether.available'
                val_balance = customer['balance']['tether']['available']
            if x['currency'] == 'DASH':
                price_atlcoin = ticker['dash_usd']
                string_query = 'balance.dash.available'
                val_balance = customer['balance']['dash']['available']
            if x['currency'] == 'EOS':
                price_atlcoin = ticker['eso_usd']
                string_query = 'balance.eos.available'
                val_balance = customer['balance']['eos']['available']
            if x['currency'] == 'ASIC':
                price_atlcoin = ticker['coin_usd']
                string_query = 'balance.coin.available'
                val_balance = customer['balance']['coin']['available']


            commission = float(x['package'])*float(percent)*float(price_atlcoin)/100

            d_wallet = float(customer['d_wallet'])
            new_d_wallet = float(d_wallet) + float(commission)
            new_d_wallet = float(new_d_wallet)

            total_earn = float(customer['total_earn'])
            new_total_earn = float(total_earn) + float(commission)
            new_total_earn = float(new_total_earn)

            balance_wallet = float(val_balance)

            new_balance_wallet = float(balance_wallet) + (float(x['package'])*float(percent)*1000000)
            new_balance_wallet = round(float(new_balance_wallet),8)

            db.users.update({ "_id" : ObjectId(customer['_id']) }, { '$set': {string_query : new_balance_wallet,'total_earn': new_total_earn, 'd_wallet' :new_d_wallet } })
            
            detail = str(percent) + '% - Ai-trade '+ str(x['package']) + ' ' + str( x['currency'])
            SaveHistory(customer['customer_id'],customer['email'],detail, round((float(x['package'])*float(percent)/100),8), x['currency'], 'Profit day')
            

            Systemcommission(customer['customer_id'],round((float(x['package'])*float(percent)/100),8),x['currency'])

            Leadership_commission(customer['customer_id'],round((float(x['package'])*float(percent)/100),8),x['currency'])

    return True

def Systemcommission(customer_id,amount_receive,currency):
    customers = db.users.find_one({"customer_id" : customer_id })
    email_customer_receive = customers['email']
    ticker = db.tickers.find_one({})
    i = 0
    while i < 12:
        i += 1 
        if customers['p_node'] != '':
            customers = db.users.find_one({"customer_id" : customers['p_node'] })
            if customers is None:
                return True
            else:
                percent_receve = 0
                if int(customers['level']) >=1 and i == 1:
                    #hoa hong dong 1 - 100%
                    percent_receve = 100
                if int(customers['level']) >=1 and i == 2:
                    #hoa hong dong 2 - 10%
                    percent_receve = 10
                if int(customers['level']) >=2 and i == 3:
                    #hoa hong dong 3 - 10%
                    percent_receve = 10
                if int(customers['level']) >=2 and i == 4:
                    #hoa hong dong 4 - 10%
                    percent_receve = 10
                if int(customers['level']) >=3 and i == 5:
                    #hoa hong dong 5 - 10%
                    percent_receve = 10
                if int(customers['level']) >=3 and i == 6:
                    #hoa hong dong 6 - 10%
                    percent_receve = 10
                if int(customers['level']) >=4 and i == 7:
                    #hoa hong dong 7 - 10%
                    percent_receve = 10
                if int(customers['level']) >=4 and i == 8:
                    #hoa hong dong 8 - 10%
                    percent_receve = 10
                if int(customers['level']) >=5 and i == 9:
                    #hoa hong dong 9 - 10%
                    percent_receve = 10
                if int(customers['level']) >=5 and i == 10:
                    #hoa hong dong 10 - 10%
                    percent_receve = 10
                if int(customers['level']) >=6 and i == 11:
                    #hoa hong dong 11 - 10%
                    percent_receve = 10
                if int(customers['level']) >=6 and i == 12:
                    #hoa hong dong 12 - 10%
                    percent_receve = 10
                if int(percent_receve) > 0:
                    
                    if currency == 'BTC': 
                        price_atlcoin = ticker['btc_usd']
                        string_query = 'balance.bitcoin.available'
                        val_balance = customers['balance']['bitcoin']['available']
                    if currency == 'ETH':
                        price_atlcoin = ticker['eth_usd']
                        string_query = 'balance.ethereum.available'
                        val_balance = customers['balance']['ethereum']['available']
                    if currency == 'LTC':
                        price_atlcoin = ticker['ltc_usd']
                        string_query = 'balance.litecoin.available'
                        val_balance = customers['balance']['litecoin']['available']
                    if currency == 'XRP':
                        price_atlcoin = ticker['xrp_usd']
                        string_query = 'balance.ripple.available'
                        val_balance = customers['balance']['ripple']['available']
                    if currency == 'USDT':
                        price_atlcoin = ticker['usdt_usd']
                        string_query = 'balance.tether.available'
                        val_balance = customers['balance']['tether']['available']
                    if currency == 'DASH':
                        price_atlcoin = ticker['dash_usd']
                        string_query = 'balance.dash.available'
                        val_balance = customers['balance']['dash']['available']
                    if currency == 'EOS':
                        price_atlcoin = ticker['eso_usd']
                        string_query = 'balance.eos.available'
                        val_balance = customers['balance']['eos']['available']
                    if currency == 'ASIC':
                        price_atlcoin = ticker['coin_usd']
                        string_query = 'balance.coin.available'
                        val_balance = customers['balance']['coin']['available']

                    

                    commission = float(amount_receive)*float(percent_receve)*float(price_atlcoin)*0.9/100

                    s_wallet = float(customers['s_wallet'])
                    new_s_wallet = float(s_wallet) + float(commission)
                    new_s_wallet = float(new_s_wallet)

                    total_earn = float(customers['total_earn'])
                    new_total_earn = float(total_earn) + float(commission)
                    new_total_earn = float(new_total_earn)

                    balance_wallet = float(val_balance)

                    new_balance_wallet = float(balance_wallet) + (float(amount_receive)*float(percent_receve)*0.9*1000000)
                    new_balance_wallet = round(float(new_balance_wallet),8)

                    db.users.update({ "_id" : ObjectId(customers['_id']) }, { '$set': {string_query : new_balance_wallet,'total_earn': new_total_earn, 's_wallet' :new_s_wallet } })
                    
                    detail = 'F'+str(i)+' '+ str(email_customer_receive) + ' received ' + str(amount_receive)+ ' ' +str( currency)
                    SaveHistory(customers['customer_id'],customers['email'],detail, round((float(amount_receive)*float(percent_receve)*0.9/100),8), currency, 'System commission')
        else:
            break
    return True



def Update_level_all_user():
    customers = db.users.find({ 'investment': { '$gt': 0 } })
    for x in customers:
        Getlevel(x['customer_id'])

    Update_league_all_user()
    return True


def Update_league_all_user():
    #League 1
    customers = db.users.find({ 'investment': { '$gt': 0 } })
    for x in customers:
        customers_child1 = db.users.find({'$and' :[{ 'level': { '$gt': 5 } },{'p_node' : x['customer_id']}]} ).count()
        if int(customers_child1) >= 2  and float(x['total_node']) >= 100000:
            if int(x['league']) < 1:
                db.users.update({ "customer_id" : x['customer_id'] }, { '$set': { "league": 1 }})

    #League 2
    customers2 = db.users.find({ 'investment': { '$gt': 0 } })
    for y in customers2:
        customers_child2 = db.users.find({'$and' :[{ 'league': { '$gt': 0 } },{'p_node' : y['customer_id']}]} ).count()
        if int(customers_child2) >= 2:
            if int(y['league']) < 2:
                db.users.update({ "customer_id" : y['customer_id'] }, { '$set': { "league": 2 }})

    #League 3
    customers3 = db.users.find({ 'investment': { '$gt': 0 } })
    for z in customers3:
        customers_child3 = db.users.find({'$and' :[{ 'league': { '$gt': 1 } },{'p_node' : z['customer_id']}]} ).count()
        if int(customers_child3) >= 2:
            if int(z['league']) < 3:
                db.users.update({ "customer_id" : z['customer_id'] }, { '$set': { "league": 3 }})

    #League 4
    customers4 = db.users.find({ 'investment': { '$gt': 0 } })
    for a in customers4:
        customers_child4 = db.users.find({'$and' :[{ 'league': { '$gt': 2 } },{'p_node' : a['customer_id']}]} ).count()
        if int(customers_child4) >= 2:
            if int(a['league']) < 4:
                db.users.update({ "customer_id" : a['customer_id'] }, { '$set': { "league": 4 }})

    #League 5
    customers5 = db.users.find({ 'investment': { '$gt': 0 } })
    for b in customers5:
        customers_child5 = db.users.find({'$and' :[{ 'league': { '$gt': 3 } },{'p_node' : b['customer_id']}]} ).count()
        if int(customers_child5) >= 2:
            if int(b['league']) < 5:
                db.users.update({ "customer_id" : b['customer_id'] }, { '$set': { "league": 5 }})

    #League 6
    customers6 = db.users.find({ 'investment': { '$gt': 0 } })
    for c in customers6:
        customers_child6 = db.users.find({'$and' :[{ 'league': { '$gt': 4 } },{'p_node' : c['customer_id']}]} ).count()
        if int(customers_child6) >= 2:
            if int(x['league']) < 6:
                db.users.update({ "customer_id" : c['customer_id'] }, { '$set': { "league": 6 }})

    return True

def Getlevel(customer_id):
    count_f1 = db.users.find({'$and' : [{"p_node" : customer_id },{ 'investment': { '$gt': 0 } }]} ).count()
    level = 0
    if int(count_f1) >= 2:
        level = 1
    if int(count_f1) >= 4:
        level = 2
    if int(count_f1) >= 6:
        level = 3
    if int(count_f1) >= 8:
        level = 4
    if int(count_f1) >= 10:
        level = 5
    if int(count_f1) >= 12:
        level = 6

    customer = db.users.find_one({"customer_id" : customer_id })
    if int(customer['level']) < level:
        db.users.update({ "customer_id" : customer_id }, { '$set': { "level": level }})
    else:
        level = customer['level']
    return level
    
def SaveHistory(uid, username,detail, amount, currency,types):
    data_history = {
        'uid':  uid,
        'username': username,
        'detail':  detail,
        'amount': round(amount,8),
        'currency' :  currency,
        'type' : types,
        'date_added' : datetime.utcnow()
    }
    db.historys.insert(data_history)
    return True

def TotalnodeAmount(user_id, amount_invest,currency):
    ticker = db.tickers.find_one({})
    customer_ml = db.users.find_one({"customer_id" : user_id })
    if currency == 'BTC': 
        price_currency = ticker['btc_usd']
        string_currency = 'btc_balance'
    if currency == 'ETH':
        price_currency = ticker['eth_usd']
        string_currency = 'eth_balance'
    if currency == 'LTC':
        price_currency = ticker['ltc_usd']
        string_currency = 'ltc_balance'
    if currency == 'XRP':
        price_currency = ticker['xrp_usd']
        string_currency = 'xrp_balance'
    if currency == 'USDT':
        price_currency = ticker['usdt_usd']
        string_currency = 'usdt_balance'
    if currency == 'EOS':
        price_currency = ticker['eos_usd']
        string_currency = 'eos_usd'
    if currency == 'DASH':
        price_currency = ticker['dash_usd']
        string_currency = 'dash_balance'

    amount_invest_usd = float(amount_invest)*float(price_currency)

    if customer_ml['p_node'] != '':
        while (True):
            customer_ml_p_node = db.users.find_one({"customer_id" : customer_ml['p_node'] })
            if customer_ml_p_node is None:
                break
            else:
                customers = db.users.find_one({"customer_id" : customer_ml_p_node['customer_id'] })
                customers['total_node'] = float(customers['total_node']) + float(amount_invest_usd)
                db.users.save(customers)
                
            # customer_ml = db.users.find_one({"customer_id" : customer_ml_p_node['customer_id'] })
            # if customer_ml is None:
                break
    return True

def Commisson_league_1(customer_id,amount_receive,currency,i,price_currency,email_customer_receive):
    if (i > 1):
        customers = db.users.find_one({"customer_id" : customer_id })
        if customers is not None:
            percent_receve = 10
            commission = float(amount_receive)*float(percent_receve)*float(price_currency)/100

            l_wallet = float(customers['l_wallet'])
            new_l_wallet = float(l_wallet) + float(commission)
            new_l_wallet = float(new_l_wallet)

            total_earn = float(customers['total_earn'])
            new_total_earn = float(total_earn) + float(commission)
            new_total_earn = float(new_total_earn)

            if currency == 'BTC': 
                string_query = 'balance.bitcoin.available'
                val_balance = customers['balance']['bitcoin']['available']
            if currency == 'ETH':
                string_query = 'balance.ethereum.available'
                val_balance = customers['balance']['ethereum']['available']
            if currency == 'LTC':
                string_query = 'balance.litecoin.available'
                val_balance = customers['balance']['litecoin']['available']
            if currency == 'XRP':
                string_query = 'balance.ripple.available'
                val_balance = customers['balance']['ripple']['available']
            if currency == 'USDT':
                string_query = 'balance.tether.available'
                val_balance = customers['balance']['tether']['available']
            if currency == 'DASH':
                string_query = 'balance.dash.available'
                val_balance = customers['balance']['dash']['available']
            if currency == 'EOS':
                string_query = 'balance.eos.available'
                val_balance = customers['balance']['eos']['available']
            if currency == 'ASIC':
                string_query = 'balance.coin.available'
                val_balance = customers['balance']['coin']['available']


            new_balance_wallet = float(val_balance) + (float(amount_receive)*float(percent_receve)*1000000)
            new_balance_wallet = round(float(new_balance_wallet),8)

            db.users.update({ "_id" : ObjectId(customers['_id']) }, { '$set': {string_query : new_balance_wallet,'total_earn': new_total_earn, 'l_wallet' :new_l_wallet } })
            
            detail = 'Receive from ID: '+ str(email_customer_receive) + ' - F'+str(i)
            SaveHistory(customers['customer_id'],customers['email'],detail, round((float(amount_receive)*float(percent_receve)/100),8), currency, 'Leader commission')
    return True
def Commisson_league_2(customer_id,amount_receive,currency,i,price_currency,email_customer_receive):
    if (i == 1):
        customers = db.users.find_one({"customer_id" : customer_id })
        if customers is not None:
            percent_receve = 10
            commission = float(amount_receive)*float(percent_receve)*float(price_currency)/100

            l_wallet = float(customers['l_wallet'])
            new_l_wallet = float(l_wallet) + float(commission)
            new_l_wallet = float(new_l_wallet)

            total_earn = float(customers['total_earn'])
            new_total_earn = float(total_earn) + float(commission)
            new_total_earn = float(new_total_earn)

            if currency == 'BTC': 
                string_query = 'balance.bitcoin.available'
                val_balance = customers['balance']['bitcoin']['available']
            if currency == 'ETH':
                string_query = 'balance.ethereum.available'
                val_balance = customers['balance']['ethereum']['available']
            if currency == 'LTC':
                string_query = 'balance.litecoin.available'
                val_balance = customers['balance']['litecoin']['available']
            if currency == 'XRP':
                string_query = 'balance.ripple.available'
                val_balance = customers['balance']['ripple']['available']
            if currency == 'USDT':
                string_query = 'balance.tether.available'
                val_balance = customers['balance']['tether']['available']
            if currency == 'DASH':
                string_query = 'balance.dash.available'
                val_balance = customers['balance']['dash']['available']
            if currency == 'EOS':
                string_query = 'balance.eos.available'
                val_balance = customers['balance']['eos']['available']
            if currency == 'ASIC':
                string_query = 'balance.coin.available'
                val_balance = customers['balance']['coin']['available']


            new_balance_wallet = float(val_balance) + (float(amount_receive)*float(percent_receve)*1000000)
            new_balance_wallet = round(float(new_balance_wallet),8)

            db.users.update({ "_id" : ObjectId(customers['_id']) }, { '$set': {string_query : new_balance_wallet,'total_earn': new_total_earn, 'l_wallet' :new_l_wallet } })
            
            detail = 'Receive from ID: '+ str(email_customer_receive) + ' - F'+str(i)
            SaveHistory(customers['customer_id'],customers['email'],detail, round((float(amount_receive)*float(percent_receve)/100),8), currency, 'Leader commission')
    return True

def Commisson_league_3(customer_id,amount_receive,currency,i,price_currency,email_customer_receive):
    if (i == 1):
        customers = db.users.find_one({"customer_id" : customer_id })
        if customers is not None:
            percent_receve = 20
            commission = float(amount_receive)*float(percent_receve)*float(price_currency)/100

            l_wallet = float(customers['l_wallet'])
            new_l_wallet = float(l_wallet) + float(commission)
            new_l_wallet = float(new_l_wallet)

            total_earn = float(customers['total_earn'])
            new_total_earn = float(total_earn) + float(commission)
            new_total_earn = float(new_total_earn)

            if currency == 'BTC': 
                string_query = 'balance.bitcoin.available'
                val_balance = customers['balance']['bitcoin']['available']
            if currency == 'ETH':
                string_query = 'balance.ethereum.available'
                val_balance = customers['balance']['ethereum']['available']
            if currency == 'LTC':
                string_query = 'balance.litecoin.available'
                val_balance = customers['balance']['litecoin']['available']
            if currency == 'XRP':
                string_query = 'balance.ripple.available'
                val_balance = customers['balance']['ripple']['available']
            if currency == 'USDT':
                string_query = 'balance.tether.available'
                val_balance = customers['balance']['tether']['available']
            if currency == 'DASH':
                string_query = 'balance.dash.available'
                val_balance = customers['balance']['dash']['available']
            if currency == 'EOS':
                string_query = 'balance.eos.available'
                val_balance = customers['balance']['eos']['available']
            if currency == 'ASIC':
                string_query = 'balance.coin.available'
                val_balance = customers['balance']['coin']['available']


            new_balance_wallet = float(val_balance) + (float(amount_receive)*float(percent_receve)*1000000)
            new_balance_wallet = round(float(new_balance_wallet),8)

            db.users.update({ "_id" : ObjectId(customers['_id']) }, { '$set': {string_query : new_balance_wallet,'total_earn': new_total_earn, 'l_wallet' :new_l_wallet } })
            
            detail = 'Receive from ID: '+ str(email_customer_receive) + ' - F'+str(i)
            SaveHistory(customers['customer_id'],customers['email'],detail, round((float(amount_receive)*float(percent_receve)/100),8), currency, 'Leader commission')
    return True

def Commisson_league_4(customer_id,amount_receive,currency,i,price_currency,email_customer_receive):
    if i == 1:
        percent_receve = 30
    else:
        percent_receve = 15
    customers = db.users.find_one({"customer_id" : customer_id })
    if customers is not None:
        
        commission = float(amount_receive)*float(percent_receve)*float(price_currency)/100

        l_wallet = float(customers['l_wallet'])
        new_l_wallet = float(l_wallet) + float(commission)
        new_l_wallet = float(new_l_wallet)

        total_earn = float(customers['total_earn'])
        new_total_earn = float(total_earn) + float(commission)
        new_total_earn = float(new_total_earn)

        if currency == 'BTC': 
            string_query = 'balance.bitcoin.available'
            val_balance = customers['balance']['bitcoin']['available']
        if currency == 'ETH':
            string_query = 'balance.ethereum.available'
            val_balance = customers['balance']['ethereum']['available']
        if currency == 'LTC':
            string_query = 'balance.litecoin.available'
            val_balance = customers['balance']['litecoin']['available']
        if currency == 'XRP':
            string_query = 'balance.ripple.available'
            val_balance = customers['balance']['ripple']['available']
        if currency == 'USDT':
            string_query = 'balance.tether.available'
            val_balance = customers['balance']['tether']['available']
        if currency == 'DASH':
            string_query = 'balance.dash.available'
            val_balance = customers['balance']['dash']['available']
        if currency == 'EOS':
            string_query = 'balance.eos.available'
            val_balance = customers['balance']['eos']['available']
        if currency == 'ASIC':
            string_query = 'balance.coin.available'
            val_balance = customers['balance']['coin']['available']


        new_balance_wallet = float(val_balance) + (float(amount_receive)*float(percent_receve)*1000000)
        new_balance_wallet = round(float(new_balance_wallet),8)

        db.users.update({ "_id" : ObjectId(customers['_id']) }, { '$set': {string_query : new_balance_wallet,'total_earn': new_total_earn, 'l_wallet' :new_l_wallet } })
        
        detail = 'Receive from ID: '+ str(email_customer_receive) + ' - F'+str(i)
        SaveHistory(customers['customer_id'],customers['email'],detail, round((float(amount_receive)*float(percent_receve)/100),8), currency, 'Leader commission')

    return True

def Commisson_league_5(customer_id,amount_receive,currency,i,price_currency,email_customer_receive):
    if i == 1:
        percent_receve = 40
    else:
        percent_receve = 18
    customers = db.users.find_one({"customer_id" : customer_id })
    if customers is not None:
        
        commission = float(amount_receive)*float(percent_receve)*float(price_currency)/100

        l_wallet = float(customers['l_wallet'])
        new_l_wallet = float(l_wallet) + float(commission)
        new_l_wallet = float(new_l_wallet)

        total_earn = float(customers['total_earn'])
        new_total_earn = float(total_earn) + float(commission)
        new_total_earn = float(new_total_earn)

        if currency == 'BTC': 
            string_query = 'balance.bitcoin.available'
            val_balance = customers['balance']['bitcoin']['available']
        if currency == 'ETH':
            string_query = 'balance.ethereum.available'
            val_balance = customers['balance']['ethereum']['available']
        if currency == 'LTC':
            string_query = 'balance.litecoin.available'
            val_balance = customers['balance']['litecoin']['available']
        if currency == 'XRP':
            string_query = 'balance.ripple.available'
            val_balance = customers['balance']['ripple']['available']
        if currency == 'USDT':
            string_query = 'balance.tether.available'
            val_balance = customers['balance']['tether']['available']
        if currency == 'DASH':
            string_query = 'balance.dash.available'
            val_balance = customers['balance']['dash']['available']
        if currency == 'EOS':
            string_query = 'balance.eos.available'
            val_balance = customers['balance']['eos']['available']
        if currency == 'ASIC':
            string_query = 'balance.coin.available'
            val_balance = customers['balance']['coin']['available']


        new_balance_wallet = float(val_balance) + (float(amount_receive)*float(percent_receve)*1000000)
        new_balance_wallet = round(float(new_balance_wallet),8)

        db.users.update({ "_id" : ObjectId(customers['_id']) }, { '$set': {string_query : new_balance_wallet,'total_earn': new_total_earn, 'l_wallet' :new_l_wallet } })
        
        detail = 'Receive from ID: '+ str(email_customer_receive) + ' - F'+str(i)
        SaveHistory(customers['customer_id'],customers['email'],detail, round((float(amount_receive)*float(percent_receve)/100),8), currency, 'Leader commission')

    return True

def Commisson_league_6(customer_id,amount_receive,currency,i,price_currency,email_customer_receive):
    if i == 1:
        percent_receve = 50
    else:
        percent_receve = 20
    customers = db.users.find_one({"customer_id" : customer_id })
    if customers is not None:
        
        commission = float(amount_receive)*float(percent_receve)*float(price_currency)/100

        l_wallet = float(customers['l_wallet'])
        new_l_wallet = float(l_wallet) + float(commission)
        new_l_wallet = float(new_l_wallet)

        total_earn = float(customers['total_earn'])
        new_total_earn = float(total_earn) + float(commission)
        new_total_earn = float(new_total_earn)

        if currency == 'BTC': 
            string_query = 'balance.bitcoin.available'
            val_balance = customers['balance']['bitcoin']['available']
        if currency == 'ETH':
            string_query = 'balance.ethereum.available'
            val_balance = customers['balance']['ethereum']['available']
        if currency == 'LTC':
            string_query = 'balance.litecoin.available'
            val_balance = customers['balance']['litecoin']['available']
        if currency == 'XRP':
            string_query = 'balance.ripple.available'
            val_balance = customers['balance']['ripple']['available']
        if currency == 'USDT':
            string_query = 'balance.tether.available'
            val_balance = customers['balance']['tether']['available']
        if currency == 'DASH':
            string_query = 'balance.dash.available'
            val_balance = customers['balance']['dash']['available']
        if currency == 'EOS':
            string_query = 'balance.eos.available'
            val_balance = customers['balance']['eos']['available']
        if currency == 'ASIC':
            string_query = 'balance.coin.available'
            val_balance = customers['balance']['coin']['available']


        new_balance_wallet = float(val_balance) + (float(amount_receive)*float(percent_receve)*1000000)
        new_balance_wallet = round(float(new_balance_wallet),8)

        db.users.update({ "_id" : ObjectId(customers['_id']) }, { '$set': {string_query : new_balance_wallet,'total_earn': new_total_earn, 'l_wallet' :new_l_wallet } })
        
        detail = 'Receive from ID: '+ str(email_customer_receive) + ' - F'+str(i)
        SaveHistory(customers['customer_id'],customers['email'],detail, round((float(amount_receive)*float(percent_receve)/100),8), currency, 'Leader commission')

    return True

def Leadership_commission(customer_id,amount_receive,currency):
    customer_ml = db.users.find_one({"customer_id" : customer_id })
    email_customer_receive = customer_ml['email']
    ticker = db.tickers.find_one({})
    if customer_ml['p_node'] != '':

        if currency == 'BTC': 
            price_currency = ticker['btc_usd']
        if currency == 'ETH':
            price_currency = ticker['eth_usd']
        if currency == 'LTC':
            price_currency = ticker['ltc_usd']
        if currency == 'XRP':
            price_currency = ticker['xrp_usd']
        if currency == 'USDT':
            price_currency = ticker['usdt_usd']
        if currency == 'EOS':
            price_currency = ticker['eos_usd']
        if currency == 'DASH':
            price_currency = ticker['dash_usd']

        i = 0
        while (True):
            i +=1
            customer_ml_p_node = db.users.find_one({"customer_id" : customer_ml['p_node'] })
            if customer_ml_p_node is None:
                break
            else:
                if int(customer_ml_p_node['league']) == 1:
                    Commisson_league_1(customer_ml_p_node['customer_id'],amount_receive,currency,i,price_currency,email_customer_receive)

                if int(customer_ml_p_node['league']) == 2:
                    Commisson_league_2(customer_ml_p_node['customer_id'],amount_receive,currency,i,price_currency,email_customer_receive)

                if int(customer_ml_p_node['league']) == 3:
                    Commisson_league_3(customer_ml_p_node['customer_id'],amount_receive,currency,i,price_currency,email_customer_receive)

                if int(customer_ml_p_node['league']) == 4:
                    Commisson_league_4(customer_ml_p_node['customer_id'],amount_receive,currency,i,price_currency,email_customer_receive)

                if int(customer_ml_p_node['league']) == 5:
                    Commisson_league_5(customer_ml_p_node['customer_id'],amount_receive,currency,i,price_currency,email_customer_receive)

                if int(customer_ml_p_node['league']) == 6:
                    Commisson_league_6(customer_ml_p_node['customer_id'],amount_receive,currency,i,price_currency,email_customer_receive)
                #print customer_ml_p_node['customer_id'],i
                
            customer_ml = db.users.find_one({"customer_id" : customer_ml_p_node['customer_id'] })
            if customer_ml is None:
                break