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

apidepist_ctrl = Blueprint('deposit', __name__, static_folder='static', template_folder='templates')

@apidepist_ctrl.route('/get-address', methods=['GET', 'POST'])
def get_address():
    dataDict = json.loads(request.data)
    
    customer_id = dataDict['customer_id']
    currency = dataDict['currency']
    

    url_callback = 'http://62.210.84.7:58011/account/jskfkjsfhkjsdhfqwtryqweqeweqeqwe'
    user = db.users.find_one({'customer_id': customer_id})
    if currency == 'BTC':
      if user['btc_address'] == '':
        respon_wallet_btc = ApiCoinpayment.get_callback_address(currency='BTC', ipn_url=url_callback)
        if respon_wallet_btc['error'] == 'ok':
          new_wallet =  respon_wallet_btc['result']['address']
          db.users.update({ "customer_id" : customer_id }, { '$set': { "btc_address": new_wallet } })
        else:
          new_wallet = ''
      else:
        new_wallet = user['btc_address']

    if currency == 'ETH':
      if user['eth_address'] == '':
        respon_wallet_btc = ApiCoinpayment.get_callback_address(currency='ETH', ipn_url=url_callback)
        if respon_wallet_btc['error'] == 'ok':
          new_wallet =  respon_wallet_btc['result']['address']
          db.users.update({ "customer_id" : customer_id }, { '$set': { "eth_address": new_wallet } })
        else:
          new_wallet = ''
      else:
        new_wallet = user['eth_address']

    if currency == 'LTC':
      if user['ltc_address'] == '':
        respon_wallet_btc = ApiCoinpayment.get_callback_address(currency='LTC', ipn_url=url_callback)
        if respon_wallet_btc['error'] == 'ok':
          new_wallet =  respon_wallet_btc['result']['address']
          db.users.update({ "customer_id" : customer_id }, { '$set': { "ltc_address": new_wallet } })
        else:
          new_wallet = ''
      else:
        new_wallet = user['ltc_address']


    if currency == 'XRP':
      if user['xrp_address'] == '':
        respon_wallet_btc = ApiCoinpayment.get_callback_address(currency='XRP', ipn_url=url_callback)
        if respon_wallet_btc['error'] == 'ok':
          new_wallet =  respon_wallet_btc['result']['address']
          db.users.update({ "customer_id" : customer_id }, { '$set': { "xrp_address": new_wallet } })
        else:
          new_wallet = ''
      else:
        new_wallet = user['xrp_address']

    if currency == 'USDT':
      if user['usdt_address'] == '':
        respon_wallet_btc = ApiCoinpayment.get_callback_address(currency='USDT', ipn_url=url_callback)
        if respon_wallet_btc['error'] == 'ok':
          new_wallet =  respon_wallet_btc['result']['address']
          db.users.update({ "customer_id" : customer_id }, { '$set': { "usdt_address": new_wallet } })
        else:
          new_wallet = ''
      else:
        new_wallet = user['usdt_address']


    if currency == 'STO':
      if user['coin_address'] == '':
        respon_wallet_btc = ApiCoinpayment.get_callback_address(currency='USDT', ipn_url=url_callback)
        if respon_wallet_btc['error'] == 'ok':
          new_wallet =  respon_wallet_btc['result']['address']
          db.users.update({ "customer_id" : customer_id }, { '$set': { "coin_address": new_wallet } })
        else:
          new_wallet = ''
      else:
        new_wallet = user['coin_address']

   
    return json.dumps({
        'status': 'complete', 
        'address': new_wallet 
    })

@apidepist_ctrl.route('/jskfkjsfhkjsdhfqwtryqweqeweqeqwe', methods=['GET', 'POST'])
def CallbackCoinPayment():
  print "callback"
  if request.method == 'POST':
    tx = request.form['txn_id'];
    address = request.form['address'];
    amount = request.form['amount'];
    currency = request.form['currency'];

    if currency == 'BTC':
      query_search = {'btc_address' : address}
    if currency == 'ETH':
      query_search = {'eth_address' : address}
    if currency == 'USDT':
      query_search = {'usdt_address' : address}
    if currency == 'XRP':
      query_search = {'xrp_address' : address}
    if currency == 'LTC':
      query_search = {'ltc_address' : address}
      
    check_deposit = db.deposits.find_one({'tx': tx})
    customer = db.users.find_one(query_search)

    if check_deposit is None and customer is not None:

      data = {
        'user_id': customer['_id'],
        'uid': customer['customer_id'],
        'username': customer['username'],
        'amount': amount,
        'type': currency,
        'tx': tx,
        'date_added' : datetime.utcnow(),
        'status': 1,
        'address': address
      }
      db.deposits.insert(data)
      if currency == 'BTC':
        new_balance_wallets = float(customer['btc_balance']) + float(amount)*100000000
        db.users.update(query_search, { '$set': { "btc_balance": float(new_balance_wallets) } })

      if currency == 'ETH':
        new_balance_wallets = float(customer['eth_balance']) + float(amount)*100000000
        db.users.update(query_search, { '$set': { "eth_balance": float(new_balance_wallets) } })

      if currency == 'LTC':
        new_balance_wallets = float(customer['ltc_balance']) + float(amount)*100000000
        db.users.update(query_search, { '$set': { "ltc_balance": float(new_balance_wallets) } })

      if currency == 'XRP':
        new_balance_wallets = float(customer['xrp_balance']) + float(amount)*100000000
        db.users.update(query_search, { '$set': { "xrp_balance": float(new_balance_wallets) } })

      if currency == 'USDT':
        new_balance_wallets = float(customer['usdt_balance']) + float(amount)*100000000
        db.users.update(query_search, { '$set': { "usdt_balance": float(new_balance_wallets) } })
      
  return json.dumps({'txid': 'complete'})

@apidepist_ctrl.route('/get-user', methods=['GET', 'POST'])
def get_user():
    dataDict = json.loads(request.data)
    customer_id = dataDict['customer_id']
    user = db.users.find_one({'customer_id': customer_id})
    return json.dumps({
        'status': 'complete', 
        'btc_balance': user['btc_balance'],
        'eth_balance': user['eth_balance'],
        'ltc_balance': user['ltc_balance'],
        'xrp_balance': user['xrp_balance'],
        'usdt_balance': user['usdt_balance'],
        'coin_balance': user['coin_balance'],
        'email': user['email'],
        'img_profile': user['img_profile']
    })


@apidepist_ctrl.route('/get-history', methods=['GET', 'POST'])
def get_history():
    dataDict = json.loads(request.data)
    customer_id = dataDict['customer_id']
    start = dataDict['start']
    limit = dataDict['limit']
    deposit = db.deposits.find({'uid': customer_id}).sort([("date_added", -1)]).limit(limit).skip(start)

    #.sort("date_added", -1)

    array = []
    for item in deposit:
      
      array.append({
        "username" : item['username'],
        "status" : item['status'],
        "amount" : item['amount'],
        "tx" : item['tx'],
        "address" : item['address'],
        "date_added" : (item['date_added']).strftime('%H:%M %d-%m-%Y'),
        "type" : item['type']
      })
    return json.dumps(array)
    