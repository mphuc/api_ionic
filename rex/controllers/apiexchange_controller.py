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

apiexchange_ctrl = Blueprint('exchange', __name__, static_folder='static', template_folder='templates')

@apiexchange_ctrl.route('/submit', methods=['GET', 'POST'])
def submit_exchange():
    dataDict = json.loads(request.data)
    customer_id = dataDict['customer_id']
    form = dataDict['form']
    to = dataDict['to']
    amount = dataDict['amount']
    
    user = db.User.find_one({'customer_id': customer_id})
    if form == 'BTC':
      val_balance = user['btc_balance']
    if form == 'ETH':
      val_balance = user['eth_balance']
    if form == 'LTC':
      val_balance = user['ltc_balance']
    if form == 'XRP':
      val_balance = user['xrp_balance']
    if form == 'USDT':
      val_balance = user['usdt_balance']
    if form == 'STO':
      val_balance = user['coin_balance']

    if float(val_balance) >= float(amount)*100000000 + float(amount)*100000000*0.0025:

      ticker = db.tickers.find_one({})

      if form == 'BTC': 
        price_form = ticker['btc_usd']
        string_from = 'btc_balance'
      if form == 'ETH':
        price_form = ticker['eth_usd']
        string_from = 'eth_balance'
      if form == 'LTC':
        price_form = ticker['ltc_usd']
        string_from = 'ltc_balance'
      if form == 'XRP':
        price_form = ticker['xrp_usd']
        string_from = 'xrp_balance'
      if form == 'USDT':
        price_form = ticker['usdt_usd']
        string_from = 'usdt_balance'
      if form == 'STO':
        price_form = ticker['coin_usd']
        string_from = 'coin_balance'

      amount_usd_form = float(amount)*float(price_form)

      if to == 'BTC': 
        price_to = ticker['btc_usd']
        string_to = 'btc_balance'
      if to == 'ETH':
        price_to = ticker['eth_usd']
        string_to = 'eth_balance'
      if to == 'LTC':
        price_to = ticker['ltc_usd']
        string_to = 'ltc_balance'
      if to == 'XRP':
        price_to = ticker['xrp_usd']
        string_to = 'xrp_balance'
      if to == 'USDT':
        price_to = ticker['usdt_usd']
        string_to = 'usdt_balance'
      if to == 'STO':
        price_to = ticker['coin_usd']
        string_to = 'coin_balance'

      balance_add = (float(amount_usd_form)/float(price_to))*100000000
      balance_sub = float(amount)*100000000 + float(amount)*100000000*0.0025

      new_balance_add = float(balance_add) + float(user[string_to])
      new_balance_sub = float(user[string_from]) - float(balance_sub)

      
      db.users.update({ "customer_id" : customer_id }, { '$set': { string_from: float(new_balance_sub) ,string_to : float(new_balance_add)} })
      
      #save lich su
      data_history = {
          'uid':  customer_id,
          'user_id': customer_id,
          'username': user['email'],
          'detail':  'exchange',
          'amount_form': float(amount),
          'amount_to' :  float(balance_add)/100000000,
          'currency_from' :  form,
          'currency_to' :  to,
          'price_form' : price_form,
          'price_to':  price_to,
          'date_added' : datetime.utcnow()
      }
      db.exchanges.insert(data_history)

      return json.dumps({
          'status': 'complete', 
          'message': 'Account successfully created' 
      })
    else:
      return json.dumps({
          'status': 'error', 
          'message': 'Your '+str(form)+' balance is not enough to exchange.' 
      })
    
@apiexchange_ctrl.route('/submit-support', methods=['GET', 'POST'])
def submit_support():
    dataDict = json.loads(request.data)
    customer_id = dataDict['customer_id']
    title = dataDict['title']
    content = dataDict['content']
    user = db.User.find_one({'customer_id': customer_id})
    data_support = {
      'user_id': customer_id,
      'username' : user['email'],
      'message': content,
      'subject': title,
      'reply': [],
      'date_added' : datetime.utcnow(),
      'status': 0
    }
    db.supports.insert(data_support)

    return json.dumps({
        'status': 'complete', 
        'message': 'Account successfully created' 
    })

@apiexchange_ctrl.route('/submit-support-reply', methods=['GET', 'POST'])
def submit_support_reply():
    dataDict = json.loads(request.data)
    _ids = dataDict['_id']
    customer_id = dataDict['customer_id']
    user = db.User.find_one({'customer_id': customer_id})
    content = dataDict['content']
    data_support = {
      'user_id': customer_id,
      'username' : user['email'],
      'message': content,
      'date_added' : datetime.utcnow()
    }
    db.supports.update({ "_id" : ObjectId(_ids) }, { '$set': { "status": 0 }, '$push':{'reply':data_support } })

    return json.dumps({
        'status': 'complete', 
        'message': 'Account successfully created' 
    })
    

@apiexchange_ctrl.route('/get-history', methods=['GET', 'POST'])
def get_historys():

    dataDict = json.loads(request.data)
    customer_id = dataDict['customer_id']
    start = dataDict['start']
    limit = dataDict['limit']
    exchanges = db.exchanges.find({'uid': customer_id}).sort([("date_added", -1)]).limit(limit).skip(start)

    #.sort("date_added", -1)

    array = []
    for item in exchanges:
      array.append({
        "username" : item['username'],
        "amount_form" : item['amount_form'],
        "amount_to" : item['amount_to'],
        "price_form" : item['price_form'],
        "price_to" : item['price_to'],
        "currency_from" :  item['currency_from'],
        "currency_to" :  item['currency_to'],
        "date_added" : (item['date_added']).strftime('%H:%M %d-%m-%Y')
      })
    return json.dumps(array)

@apiexchange_ctrl.route('/get-history-transaction', methods=['GET', 'POST'])
def get_history_transaction():

    dataDict = json.loads(request.data)
    customer_id = dataDict['customer_id']
    start = dataDict['start']
    limit = dataDict['limit']
    
    history = db.historys.find({'$and' : [{'uid': customer_id}]}).sort([("date_added", -1)]).limit(limit).skip(start)
    #.sort("date_added", -1)

    array = []
    for item in history:
      array.append({
        "username" : item['username'],
        "amount" : item['amount'],
        "amount" : item['amount'],
        "type" : item['type'],
        "date_added" : (item['date_added']).strftime('%H:%M %d-%m-%Y')
      })
    return json.dumps(array)

@apiexchange_ctrl.route('/get-history-support', methods=['GET', 'POST'])
def get_history_support():

    dataDict = json.loads(request.data)
    customer_id = dataDict['customer_id']
    start = dataDict['start']
    limit = dataDict['limit']
    
    support = db.supports.find({'$and' : [{'user_id': customer_id}]}).sort([("date_added", -1)]).limit(limit).skip(start)
    #.sort("date_added", -1)

    array = []
    for item in support:
      array.append({
        "_id" : str(item['_id']),
        "username" : item['username'],
        "message" : item['message'],
        "subject" : item['subject'],
        "status" : item['status'],
        "date_added" : (item['date_added']).strftime('%H:%M %d-%m-%Y')
      })
    return json.dumps(array)

@apiexchange_ctrl.route('/get-support-id', methods=['GET', 'POST'])
def get_support_id():

    dataDict = json.loads(request.data)
    _ids = dataDict['_id']
    
    item = db.supports.find_one({'_id' :  ObjectId(_ids)})
    reply = []
    for  x in item['reply']  :
      reply.append({
        "username" : (x['username']),
        "message" : x['message'],
        "user_id" : x['user_id'],
        "date_added" : (x['date_added']).strftime('%H:%M %d-%m-%Y')
      })

    return json.dumps({
        "_id" : str(item['_id']),
        "username" : item['username'],
        "message" : item['message'],
        "subject" : item['subject'],
        "status" : item['status'],
        "reply" : reply,
        "date_added" : (item['date_added']).strftime('%H:%M %d-%m-%Y')
      })


@apiexchange_ctrl.route('/load-price', methods=['GET', 'POST'])
def load_price():
    ticker = db.tickers.find_one({})
    
    return json.dumps({
        'status': 'complete', 
        'btc_usd': ticker['btc_usd'],
        'eth_usd': ticker['eth_usd'],
        'ltc_usd': ticker['ltc_usd'],
        'xrp_usd': ticker['xrp_usd'],
        'coin_usd': ticker['coin_usd'],
        'usdt_usd': ticker['usdt_usd']
    })
    
@apiexchange_ctrl.route('/get-member', methods=['GET', 'POST'])
def get_member():

    dataDict = json.loads(request.data)
    customer_id = dataDict['customer_id']
    start = dataDict['start']
    limit = dataDict['limit']
    member = db.users.find({'p_node': customer_id}).sort([("creation", -1)]).limit(limit).skip(start)

    #.sort("date_added", -1)

    array = []
    for item in member:
      array.append({
        "customer_id" : item['customer_id'],
        "email" : item['email'],
        "level" : item['level'],
        "img_profile" : item['img_profile'],
        "active_email" : item['active_email'],
        "date_added" : (item['creation']).strftime('%H:%M %d-%m-%Y')
      })
    return json.dumps(array)

@apiexchange_ctrl.route('/get-infomation-user', methods=['GET', 'POST'])
def get_infomation_user():

    dataDict = json.loads(request.data)
    customer_id = dataDict['customer_id']
    
    user = db.users.find_one({'customer_id': customer_id})
    if user is not None:
      return json.dumps({
          'status': 'complete', 
          'email': user['email'],
          'date_added' : (user['creation']).strftime('%H:%M %d-%m-%Y'),
          'investment': user['investment'],
          'img_profile' : user['img_profile']
      })
    else:
      return json.dumps({
          'status': 'error'
      })
   
