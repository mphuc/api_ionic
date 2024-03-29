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
def check_password(pw_hash, password):
        return check_password_hash(pw_hash, password)
@apidepist_ctrl.route('/get-address', methods=['GET', 'POST'])
def get_address():
    dataDict = json.loads(request.data)
    
    customer_id = dataDict['customer_id']
    currency = dataDict['currency']
    

    url_callback = 'http://62.210.84.7:58011/account/jskfkjsfhkjsdhfqwtryqweqeweqeqwe'
    user = db.users.find_one({'customer_id': customer_id})
    if currency == 'BTC':
      if user['balance']['bitcoin']['cryptoaddress'] == '':
        respon_wallet_btc = ApiCoinpayment.get_callback_address(currency='BTC', ipn_url=url_callback)
        if respon_wallet_btc['error'] == 'ok':
          new_wallet =  respon_wallet_btc['result']['address']
          if len(new_wallet.split("coinpaymt")) > 1:
            new_wallet = ''
          db.users.update({ "customer_id" : customer_id }, { '$set': { "balance.bitcoin.cryptoaddress": new_wallet } })
        else:
          new_wallet = ''
      else:
        new_wallet = user['balance']['bitcoin']['cryptoaddress']

    if currency == 'ETH':
      if user['balance']['ethereum']['cryptoaddress'] == '':
        respon_wallet_btc = ApiCoinpayment.get_callback_address(currency='ETH', ipn_url=url_callback)
        if respon_wallet_btc['error'] == 'ok':
          new_wallet =  respon_wallet_btc['result']['address']
          if len(new_wallet.split("coinpaymt")) > 1:
            new_wallet = ''
          db.users.update({ "customer_id" : customer_id }, { '$set': { "balance.ethereum.cryptoaddress": new_wallet } })
        else:
          new_wallet = ''
      else:
        new_wallet = user['balance']['ethereum']['cryptoaddress']

    if currency == 'LTC':
      if user['balance']['litecoin']['cryptoaddress'] == '':
        respon_wallet_btc = ApiCoinpayment.get_callback_address(currency='LTC', ipn_url=url_callback)
        if respon_wallet_btc['error'] == 'ok':
          new_wallet =  respon_wallet_btc['result']['address']
          if len(new_wallet.split("coinpaymt")) > 1:
            new_wallet = ''
          db.users.update({ "customer_id" : customer_id }, { '$set': { "balance.litecoin.cryptoaddress": new_wallet } })
        else:
          new_wallet = ''
      else:
        new_wallet = user['balance']['litecoin']['cryptoaddress']


    if currency == 'XRP':
      if user['balance']['ripple']['cryptoaddress'] == '':
        respon_wallet_btc = ApiCoinpayment.get_callback_address(currency='XRP', ipn_url=url_callback)
        if respon_wallet_btc['error'] == 'ok':
          new_wallet =  respon_wallet_btc['result']['address']
          if len(new_wallet.split("coinpaymt")) > 1:
            new_wallet = ''
          db.users.update({ "customer_id" : customer_id }, { '$set': { "balance.ripple.cryptoaddress": new_wallet } })
        else:
          new_wallet = ''
      else:
        new_wallet = user['balance']['ripple']['cryptoaddress']

    if currency == 'USDT':
      if user['balance']['tether']['cryptoaddress'] == '':
        respon_wallet_btc = ApiCoinpayment.get_callback_address(currency='USDT', ipn_url=url_callback)
        if respon_wallet_btc['error'] == 'ok':
          new_wallet =  respon_wallet_btc['result']['address']
          if len(new_wallet.split("coinpaymt")) > 1:
            new_wallet = ''
          db.users.update({ "customer_id" : customer_id }, { '$set': { "balance.tether.cryptoaddress": new_wallet } })
        else:
          new_wallet = ''
      else:
        new_wallet = user['balance']['tether']['cryptoaddress']


    if currency == 'EOS':
      if user['balance']['eos']['cryptoaddress'] == '':
        respon_wallet_btc = ApiCoinpayment.get_callback_address(currency='EOS', ipn_url=url_callback)
        if respon_wallet_btc['error'] == 'ok':
          new_wallet =  respon_wallet_btc['result']['address']
          if len(new_wallet.split("coinpaymt")) > 1:
            new_wallet = ''
          db.users.update({ "customer_id" : customer_id }, { '$set': { "balance.eos.cryptoaddress": new_wallet } })
        else:
          new_wallet = ''
      else:
        new_wallet = user['balance']['eos']['cryptoaddress']

    if currency == 'DASH':
      if user['balance']['dash']['cryptoaddress'] == '':
        respon_wallet_btc = ApiCoinpayment.get_callback_address(currency='DASH', ipn_url=url_callback)
        if respon_wallet_btc['error'] == 'ok':
          new_wallet =  respon_wallet_btc['result']['address']
          if len(new_wallet.split("coinpaymt")) > 1:
            new_wallet = ''
          db.users.update({ "customer_id" : customer_id }, { '$set': { "balance.dash.cryptoaddress": new_wallet } })
        else:
          new_wallet = ''
      else:
        new_wallet = user['balance']['dash']['cryptoaddress']

    if currency == 'ASIC':
      new_wallet = ''
      # if user['balance']['coin']['cryptoaddress'] == '':
      #   respon_wallet_btc = ApiCoinpayment.get_callback_address(currency='ASIC', ipn_url=url_callback)
      #   if respon_wallet_btc['error'] == 'ok':
      #     new_wallet =  respon_wallet_btc['result']['address']
      #     db.users.update({ "customer_id" : customer_id }, { '$set': { "balance.coin.cryptoaddress": new_wallet } })
      #   else:
      #     new_wallet = ''
      # else:
      #   new_wallet = user['balance']['coin']['cryptoaddress']
    
    
    if len(new_wallet.split("coinpaymt")) > 1 or new_wallet == '':
        return json.dumps({
            'status': 'error', 
            'message': 'The system is maintenance. Please come back later.' 
        })

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

    ticker = db.tickers.find_one({})

    if currency == 'BTC':
      query_search = {'balance.bitcoin.cryptoaddress' : address}
      price = ticker['btc_usd']
    if currency == 'ETH':
      query_search = {'balance.ethereum.cryptoaddress' : address}
      price = ticker['eth_usd']
    if currency == 'USDT':
      query_search = {'balance.tether.cryptoaddress' : address}
      price = ticker['usdt_usd']
    if currency == 'XRP':
      query_search = {'balance.ripple.cryptoaddress' : address}
      price = ticker['xrp_usd']
    if currency == 'LTC':
      query_search = {'balance.litecoin.cryptoaddress' : address}
      price = ticker['ltc_usd']
    if currency == 'EOS':
      query_search = {'balance.eos.cryptoaddress' : address}
      price = ticker['eos_usd']
    if currency == 'DASH':
      query_search = {'balance.dash.cryptoaddress' : address}
      price = ticker['dash_usd']
      
    check_wallet = db.wallets.find_one({'$and' : [{'txt_id': tx},{'type' : 'deposit'}]} )
    customer = db.users.find_one(query_search)

    if check_wallet is None and customer is not None:

      data = {
        'user_id': customer['_id'],
        'uid': customer['customer_id'],
        'username': customer['username'],
        'amount': round(amount,8),
        'type': 'deposit',
        'txt_id': tx,
        'date_added' : datetime.utcnow(),
        'status': 1,
        'address': address,
        'currency' : currency,
        'confirmations' : 0,
        'amount_usd': float(price) * float(amount),
        'price' : price,
      }
      db.wallets.insert(data)
      if currency == 'BTC':
        new_balance_wallets = float(customer['balance']['bitcoin']['available']) + float(amount)*100000000
        db.users.update(query_search, { '$set': { "balance.bitcoin.available": float(new_balance_wallets) } })

      if currency == 'ETH':
        new_balance_wallets = float(customer['balance']['ethereum']['available']) + float(amount)*100000000
        db.users.update(query_search, { '$set': { "balance.ethereum.available": float(new_balance_wallets) } })

      if currency == 'LTC':
        new_balance_wallets = float(customer['balance']['litecoin']['available']) + float(amount)*100000000
        db.users.update(query_search, { '$set': { "balance.litecoin.available": float(new_balance_wallets) } })

      if currency == 'XRP':
        new_balance_wallets = float(customer['balance']['ripple']['available']) + float(amount)*100000000
        db.users.update(query_search, { '$set': { "balance.ripple.available": float(new_balance_wallets) } })

      if currency == 'USDT':
        new_balance_wallets = float(customer['balance']['tether']['available']) + float(amount)*100000000
        db.users.update(query_search, { '$set': { "balance.tether.available": float(new_balance_wallets) } })
      
      if currency == 'EOS':
        new_balance_wallets = float(customer['balance']['eos']['available']) + float(amount)*100000000
        db.users.update(query_search, { '$set': { "balance.eos.available": float(new_balance_wallets) } })
      
      if currency == 'DASH':
        new_balance_wallets = float(customer['balance']['dash']['available']) + float(amount)*100000000
        db.users.update(query_search, { '$set': { "balance.dash.available": float(new_balance_wallets) } })
      
  return json.dumps({'txid': 'complete'})

@apidepist_ctrl.route('/get-history-currency', methods=['GET', 'POST'])
def get_history_currency():
    dataDict = json.loads(request.data)
    customer_id = dataDict['customer_id']
    currency = dataDict['currency']
    start = dataDict['start']
    limit = dataDict['limit']
    types = dataDict['types']
    list_wallet = db.wallets.find({'$and' : [{'type' : types},{'uid': customer_id},{'currency': currency}]}).sort([("date_added", -1)]).limit(limit).skip(start)
    array = []
    for item in list_wallet:
      
      array.append({
        "username" : item['username'],
        "status" : item['status'],
        "amount" : item['amount'],
        "txt_id" : item['txt_id'],
        "address" : item['address'],
        "date_added" : (item['date_added']).strftime('%H:%M %d-%m-%Y'),
        "type" : item['type'],
        "currency" : item['currency'],
        "confirmations" : item['confirmations'],
        "amount_usd" : item['amount_usd'],
        "price" : item['price']
      })

    return json.dumps(array)
    
@apidepist_ctrl.route('/add-wallet-address', methods=['GET', 'POST'])
def add_wallet_address():
    dataDict = json.loads(request.data)
    customer_id = dataDict['customer_id']
    name = dataDict['name']
    address = dataDict['address']
    currency = dataDict['currency']
    password_transaction = dataDict['password_transaction']

    customer = db.users.find_one({'customer_id' : customer_id})

    check_name = db.contacts.find_one({'$and' : [{'customer_id' : customer_id},{'name': name},{'currency': currency}]})
    check_address = db.contacts.find_one({'$and' : [{'customer_id' : customer_id},{'address': address},{'currency': currency}]})
    if check_name is None:
        if check_address is None:
            if check_password(customer['password_transaction'], password_transaction) == True:

                data = {
                    'uid': customer['customer_id'],
                    'username': customer['username'],
                    'name': name,
                    'address':  address,
                    'currency': currency,
                    'date_added' : datetime.utcnow(),
                    'status': 0
                  }
                db.contacts.insert(data)
                return json.dumps({
                  'status': 'complete', 
                  'message': 'Add success' 
                })
            else:
                return json.dumps({
                  'status': 'error', 
                  'message': 'Wrong password transaction. Please try again' 
                })
        else:
            return json.dumps({
              'status': 'error', 
              'message': 'Address already exists. Please try again' 
            })
    else:
        return json.dumps({
          'status': 'error', 
          'message': 'Name already exists. Please try again' 
        })
            
@apidepist_ctrl.route('/get-contact-currency', methods=['GET', 'POST'])
def get_contact_currency():

    dataDict = json.loads(request.data)
    customer_id = dataDict['customer_id']
    currency = dataDict['currency']
    
    contact = db.contacts.find({'$and' : [{'uid': customer_id},{'currency' : currency}]}).sort([("date_added", -1)])

    array = []
    for item in contact:
      array.append({
        'uid': item['uid'],
        'username': item['username'],
        'name': item['name'],
        'address':  item['address'],
        'currency': item['currency'],
        'date_added' : (item['date_added']).strftime('%H:%M %d-%m-%Y'),
        'status': item['status']
      })
    return json.dumps(array)


@apidepist_ctrl.route('/withdraw-currency', methods=['GET', 'POST'])
def withdraw_currency():
    dataDict = json.loads(request.data)
    customer_id = dataDict['customer_id']
    currency = dataDict['currency']
    amount = dataDict['amount']
    address = dataDict['address']
    password_transaction = dataDict['password_transaction']

    user = db.User.find_one({'customer_id': customer_id})

    if user is not None:
      if int(user['security']['email']['status']) == 1:

        ticker = db.tickers.find_one({})
        if currency == 'BTC':
          val_balance = user['balance']['bitcoin']['available']
          price_atlcoin = ticker['btc_usd']
          string_query = 'balance.bitcoin.available'
        if currency == 'ETH':
          val_balance = user['balance']['ethereum']['available']
          price_atlcoin = ticker['eth_usd']
          string_query = 'balance.ethereum.available'
        if currency == 'LTC':
          val_balance = user['balance']['litecoin']['available']
          price_atlcoin = ticker['ltc_usd']
          string_query = 'balance.litecoin.available'
        if currency == 'XRP':
          val_balance = user['balance']['ripple']['available']
          price_atlcoin = ticker['xrp_usd']
          string_query = 'balance.ripple.available'
        if currency == 'USDT':
          val_balance = user['balance']['tether']['available']
          price_atlcoin = ticker['usdt_usd']
          string_query = 'balance.tether.available'
        if currency == 'DASH':
          val_balance = user['balance']['dash']['available']
          price_atlcoin = ticker['dash_usd']
          string_query = 'balance.dash.available'
        if currency == 'EOS':
          val_balance = user['balance']['eos']['available']
          price_atlcoin = ticker['eos_usd']
          string_query = 'balance.eos.available'
        if currency == 'ASIC':
          val_balance = user['balance']['coin']['available']
          price_atlcoin = ticker['coin_usd']
          string_query = 'balance.coin.available'

        if (float(price_atlcoin) * float(amount)) > 50:

            if check_password(user['password_transaction'], password_transaction) == True:
                print val_balance,float(amount)*100000000
                if float(val_balance) >= float(amount)*100000000:
                  if float(user['balance']['coin']['available']) >= 100000:


                    amount_usd = float(amount)*float(price_atlcoin)
                    
                    new_balance_sub = round(float(val_balance) - (float(amount)*100000000),8)

                    db.users.update({ "customer_id" : customer_id }, { '$set': { string_query: float(new_balance_sub) } })
                    
                    #save lich su
                    data = {
                      'user_id': user['_id'],
                      'uid': user['customer_id'],
                      'username': user['username'],
                      'amount': float(amount),
                      'type': 'withdraw',
                      'txt_id': '<span class="pending">Pending</span>',
                      'date_added' : datetime.utcnow(),
                      'status': 0,
                      'address': address,
                      'currency' : currency,
                      'confirmations' : 0,
                      'amount_usd': float(price_atlcoin) * float(amount),
                      'price' : price_atlcoin,
                    }
                    db.wallets.insert(data)
                    #fee
                    userss = db.User.find_one({'customer_id': customer_id})
                    new_coin_fee = round((float(userss['balance']['coin']['available']) - 100000),8)
                    db.users.update({ "customer_id" : customer_id }, { '$set': { 'balance.coin.available' : new_coin_fee } })
           
                    return json.dumps({
                        'status': 'complete', 
                        'message': 'Withdraw successfully' 
                    })
                  else:
                    return json.dumps({
                        'status': 'error',
                        'message': 'You do not have enough 0.001 ASIC to make transaction fees.' 
                    })
                else:
                  return json.dumps({
                      'status': 'error',
                      'message': 'Your account balance is not enough.' 
                  })
            else:
                return json.dumps({
                  'status': 'error', 
                  'message': 'Wrong password transaction. Please try again.' 
                })
        else:
            return json.dumps({
                'status': 'error',
                'message': 'The withdrawal number must be greater than '+str(round(50/float(price_atlcoin),8))+' '+currency
            })

      else:
        return json.dumps({
            'status': 'error',
            'message': 'Your account has not been verify.' 
        })
    else:
      return json.dumps({
          'status': 'error'
      })

