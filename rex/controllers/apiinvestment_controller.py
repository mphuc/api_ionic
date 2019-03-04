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

@apiinvestment_ctrl.route('/testinvest', methods=['GET', 'POST'])
def testinvest():
    FnRefferalProgram('3201943430', '0.1', 'BTC')
    return json.dumps({
        'status': 'complete' 
        
    })
@apiinvestment_ctrl.route('/active-package', methods=['GET', 'POST'])
def active_package():
    dataDict = json.loads(request.data)
    customer_id = dataDict['customer_id']
    currency = dataDict['currency']
    amount = dataDict['amount']
    
    user = db.User.find_one({'customer_id': customer_id})
    if user is not None:
      ticker = db.tickers.find_one({})
      if currency == 'BTC':
        val_balance = user['btc_balance']
        price_atlcoin = ticker['btc_usd']
        string_query = 'btc_balance'
      if currency == 'ETH':
        val_balance = user['eth_balance']
        price_atlcoin = ticker['eth_usd']
        string_query = 'eth_balance'
      if currency == 'LTC':
        val_balance = user['ltc_balance']
        price_atlcoin = ticker['ltc_usd']
        string_query = 'ltc_balance'
      if currency == 'XRP':
        val_balance = user['xrp_balance']
        price_atlcoin = ticker['xrp_usd']
        string_query = 'xrp_balance'
      if currency == 'USDT':
        val_balance = user['usdt_balance']
        price_atlcoin = ticker['usdt_usd']
        string_query = 'usdt_balance'
      if currency == 'STO':
        val_balance = user['coin_balance']
        price_atlcoin = ticker['coin_usd']
        string_query = 'coin_balance'

      if float(val_balance) >= float(amount)*100000000:
        amount_usd = float(amount)*float(price_atlcoin)
        
        new_balance_sub = float(user[string_query]) - float(amount)*100000000

      
        db.users.update({ "customer_id" : customer_id }, { '$set': { string_query: float(new_balance_sub)} })
        
        #save lich su
        data_investment = {
            'uid' : customer_id,
            'user_id': customer_id,
            'username' : user['email'],
            'amount_usd' : float(amount_usd),
            'package': float(amount),
            'status' : 1,
            'date_added' : datetime.utcnow(),
            'amount_frofit' : 0,
            'coin_amount' : 0,
            'total_income' : '',
            'status_income' : 0,
            'date_income' : '',
            'date_profit' : datetime.utcnow() + timedelta(days=3),
            'currency' : currency
        }
        db.investments.insert(data_investment)

        return json.dumps({
            'status': 'complete', 
            'message': 'Investment successfully' 
        })
      else:
        return json.dumps({
            'status': 'error',
            'message': 'Account balance is not enough to invest' 
        })

    else:
      return json.dumps({
          'status': 'error'
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
        "amount_usd" : item['amount_usd'],
        "date_added" : (item['date_added']).strftime('%H:%M %d-%m-%Y')
      })
    return json.dumps(array)

@apiinvestment_ctrl.route('/get-history-withdraw', methods=['GET', 'POST'])
def get_history_withdraw():

    dataDict = json.loads(request.data)
    customer_id = dataDict['customer_id']
    start = dataDict['start']
    limit = dataDict['limit']

    withdrawal = db.withdrawal.find({'uid': customer_id}).sort([("date_added", -1)]).limit(limit).skip(start)

    array = []
    # data = [json.dumps(item, default=json_util.default) for item in withdrawal]
    # return jsonify(data = data)
    # return jsonify(data = withdrawal)
    for item in withdrawal:
      array.append({
        "_id" : str(item['_id']),
        "username" : item['username'],
        "amount" : item['amount'],
        "currency" : item['currency'],
        "amount_usd" : item['amount_usd'],
        "status" : item['status'],
        "txtid" : item['txtid'],
        "date_added" : (item['date_added']).strftime('%H:%M %d-%m-%Y')
      })
    return json.dumps(array)

@apiinvestment_ctrl.route('/get-detail-withdraw', methods=['GET', 'POST'])
def get_detail_withdraw():

    dataDict = json.loads(request.data)
    _id = dataDict['_id']
    
    item = db.withdrawal.find_one({'_id': ObjectId(_id)})
    
    return json.dumps( {
        "_id" : str(item['_id']),
        "username" : item['username'],
        "amount" : item['amount'],
        "currency" : item['currency'],
        "amount_usd" : item['amount_usd'],
        "status" : item['status'],
        "txtid" : item['txtid'],
        "wallet" : item['wallet'],
        "date_added" : (item['date_added']).strftime('%H:%M %d-%m-%Y')
    })


@apiinvestment_ctrl.route('/withdraw-submit', methods=['GET', 'POST'])
def withdraw_submit():
    dataDict = json.loads(request.data)
    customer_id = dataDict['customer_id']
    currency = dataDict['currency']
    amount = dataDict['amount']
    wallet = dataDict['wallet']
    
    user = db.User.find_one({'customer_id': customer_id})
    if user is not None:
      ticker = db.tickers.find_one({})
      if currency == 'BTC':
        val_balance = user['btc_balance']
        price_atlcoin = ticker['btc_usd']
        string_query = 'btc_balance'
      if currency == 'ETH':
        val_balance = user['eth_balance']
        price_atlcoin = ticker['eth_usd']
        string_query = 'eth_balance'
      if currency == 'LTC':
        val_balance = user['ltc_balance']
        price_atlcoin = ticker['ltc_usd']
        string_query = 'ltc_balance'
      if currency == 'XRP':
        val_balance = user['xrp_balance']
        price_atlcoin = ticker['xrp_usd']
        string_query = 'xrp_balance'
      if currency == 'USDT':
        val_balance = user['usdt_balance']
        price_atlcoin = ticker['usdt_usd']
        string_query = 'usdt_balance'
      if currency == 'STO':
        val_balance = user['coin_balance']
        price_atlcoin = ticker['coin_usd']
        string_query = 'coin_balance'

      if float(val_balance) >= float(amount)*100000000:
        amount_usd = float(amount)*float(price_atlcoin)
        
        new_balance_sub = float(user[string_query]) - float(amount)*100000000

      
        db.users.update({ "customer_id" : customer_id }, { '$set': { string_query: float(new_balance_sub)} })
        
        #save lich su
        dta_withdraw = {
            'uid':  customer_id,
            'amount' :  float(amount),
            'amount_usd' : float(amount_usd),
            'wallet' : wallet,
            'txtid':  '',
            'status': 0,
            'username' : user['username'],
            'currency' : currency,
            'date_added' : datetime.utcnow(),
            'code_active' : '',
            'active_email' : '',
            'id_withdraw': ''
        }
        withdraw_id = db.withdrawal.insert(dta_withdraw)

        return json.dumps({
            'status': 'complete', 
            'message': 'Withdraw successfully' 
        })
      else:
        return json.dumps({
            'status': 'error',
            'message': 'Your account balance is not enough' 
        })

    else:
      return json.dumps({
          'status': 'error'
      })


def FnRefferalProgram(customer_id, amount_invest, currency):
    customers = db.users.find_one({"customer_id" : customer_id })
    if customers['p_node'] != '0' or customers['p_node'] != '':
        customers_pnode = db.users.find_one({"customer_id" : customers['p_node'] })

        ticker = db.tickers.find_one({})

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
        
        commission = float(price_currency)*float(amount_invest)*0.03

        r_wallet = float(customers_pnode['r_wallet'])
        new_r_wallet = float(r_wallet) + float(commission)
        new_r_wallet = float(new_r_wallet)

        total_earn = float(customers_pnode['total_earn'])
        new_total_earn = float(total_earn) + float(commission)
        new_total_earn = float(new_total_earn)

        balance_wallet = float(customers_pnode[string_currency])
        new_balance_wallet = float(balance_wallet) + (float(amount_invest)*0.03*100000000)
        new_balance_wallet = float(new_balance_wallet)

        

        db.users.update({ "_id" : ObjectId(customers_pnode['_id']) }, { '$set': {string_currency : new_balance_wallet,'total_earn': new_total_earn, 'r_wallet' :new_r_wallet } })
        
        detail = 'Account '+ str(customers['email']) + ' join the package '+ str(amount_invest) + ' ' + str(currency)
        SaveHistory(customers_pnode['customer_id'],customers_pnode['username'],detail, float(amount_invest)*0.03, currency, 'Direct commission')
   
    return True


def SaveHistory(uid, username,detail, amount, currency,types):
    data_history = {
        'uid':  uid,
        'username': username,
        'detail':  detail,
        'amount': amount,
        'currency' :  currency,
        'type' : types,
        'date_added' : datetime.utcnow()
    }
    db.historys.insert(data_history)
    return True