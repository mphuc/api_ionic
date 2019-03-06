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
    Update_league_all_user()
    #Systemcommission('32019433964','1','BTC')
    #Getlevel('32019433963')
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

      
        db.users.update({ "customer_id" : customer_id }, { '$set': { string_query: float(new_balance_sub),'investment' : amount_usd} })
        
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

        #save lich su
        data_dialing = {
            'customer_id' : customer_id,
            'username' : user['email'],
            'package': float(amount),
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
    if customers['p_node'] != '':
        customers_pnode = db.users.find_one({"customer_id" : customers['p_node'] })

        if float(customers_pnode['investment'] > 0):
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
            SaveHistory(customers_pnode['customer_id'],customers_pnode['email'],detail, float(amount_invest)*0.03, currency, 'Direct commission')
   
    return True

def caculator_profitDaily():
    
    get_percent = db.profits.find_one({});
    percent = get_percent['percent']

    get_invest = db.investments.find({ "status": 1});
    ticker = db.tickers.find_one({})
    for x in get_invest:
        
        if x['currency'] == 'BTC': 
            price_currency = ticker['btc_usd']
            string_currency = 'btc_balance'
        if x['currency'] == 'ETH':
            price_currency = ticker['eth_usd']
            string_currency = 'eth_balance'
        if x['currency'] == 'LTC':
            price_currency = ticker['ltc_usd']
            string_currency = 'ltc_balance'
        if x['currency'] == 'XRP':
            price_currency = ticker['xrp_usd']
            string_currency = 'xrp_balance'
        if x['currency'] == 'USDT':
            price_currency = ticker['usdt_usd']
            string_currency = 'usdt_balance'

        commission = float(x['package'])*float(percent)*float(price_currency)/100
       
        
        customer = db.users.find_one({'customer_id': x['uid']})
        if customer is not None:

            d_wallet = float(customer['d_wallet'])
            new_d_wallet = float(d_wallet) + float(commission)
            new_d_wallet = float(new_d_wallet)

            total_earn = float(customer['total_earn'])
            new_total_earn = float(total_earn) + float(commission)
            new_total_earn = float(new_total_earn)

            balance_wallet = float(customer[string_currency])

            new_balance_wallet = float(balance_wallet) + (float(x['package'])*float(percent)*1000000)
            new_balance_wallet = float(new_balance_wallet)

            db.users.update({ "_id" : ObjectId(customer['_id']) }, { '$set': {string_currency : new_balance_wallet,'total_earn': new_total_earn, 'd_wallet' :new_d_wallet } })
            
            detail = 'Received '+ str(percent) + '% of package '+ str(x['package']) + ' ' + str( x['currency'])
            SaveHistory(customer['customer_id'],customer['email'],detail, float(x['package'])*float(percent)/100, x['currency'], 'Profit day')
            

            Systemcommission(customer['customer_id'],float(x['package'])*float(percent)/100,x['currency'])

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
                if Getlevel(customers['customer_id']) >=1 and i == 1:
                    #hoa hong dong 1 - 100%
                    percent_receve = 100
                if Getlevel(customers['customer_id']) >=1 and i == 2:
                    #hoa hong dong 2 - 10%
                    percent_receve = 10
                if Getlevel(customers['customer_id']) >=2 and i == 3:
                    #hoa hong dong 3 - 10%
                    percent_receve = 10
                if Getlevel(customers['customer_id']) >=2 and i == 4:
                    #hoa hong dong 4 - 10%
                    percent_receve = 10
                if Getlevel(customers['customer_id']) >=3 and i == 5:
                    #hoa hong dong 5 - 10%
                    percent_receve = 10
                if Getlevel(customers['customer_id']) >=3 and i == 6:
                    #hoa hong dong 6 - 10%
                    percent_receve = 10
                if Getlevel(customers['customer_id']) >=4 and i == 7:
                    #hoa hong dong 7 - 10%
                    percent_receve = 10
                if Getlevel(customers['customer_id']) >=4 and i == 8:
                    #hoa hong dong 8 - 10%
                    percent_receve = 10
                if Getlevel(customers['customer_id']) >=5 and i == 9:
                    #hoa hong dong 9 - 10%
                    percent_receve = 10
                if Getlevel(customers['customer_id']) >=5 and i == 10:
                    #hoa hong dong 10 - 10%
                    percent_receve = 10
                if Getlevel(customers['customer_id']) >=6 and i == 11:
                    #hoa hong dong 11 - 10%
                    percent_receve = 10
                if Getlevel(customers['customer_id']) >=6 and i == 12:
                    #hoa hong dong 12 - 10%
                    percent_receve = 10
                if int(percent_receve) > 0:
                    print i

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

                    commission = float(amount_receive)*float(percent_receve)*float(price_currency)*0.9/100

                    s_wallet = float(customers['s_wallet'])
                    new_s_wallet = float(s_wallet) + float(commission)
                    new_s_wallet = float(new_s_wallet)

                    total_earn = float(customers['total_earn'])
                    new_total_earn = float(total_earn) + float(commission)
                    new_total_earn = float(new_total_earn)

                    balance_wallet = float(customers[string_currency])

                    new_balance_wallet = float(balance_wallet) + (float(amount_receive)*float(percent_receve)*0.9*1000000)
                    new_balance_wallet = float(new_balance_wallet)

                    db.users.update({ "_id" : ObjectId(customers['_id']) }, { '$set': {string_currency : new_balance_wallet,'total_earn': new_total_earn, 's_wallet' :new_s_wallet } })
                    
                    detail = 'F'+str(i)+' '+ str(email_customer_receive) + ' received ' + str(amount_receive)+ ' ' +str( currency) +' daily interest.'
                    SaveHistory(customers['customer_id'],customers['email'],detail, float(amount_receive)*float(percent_receve)*0.9/100, currency, 'System commission')
        else:
            break
    return True

# def Leadership_commission(customer_id,amount_receive,currency):
#     customers = db.users.find_one({"customer_id" : customer_id })
#     email_customer_receive = customers['email']
#     ticker = db.tickers.find_one({})


def Update_league_all_user():
    db.users.update({ }, { '$set': { "league": 0 }},multi=True)
    #League 1
    customers = db.users.find({ 'level': { '$gt': 0 } })
    for x in customers:
        customers_child1 = db.users.find({'$and' :[{ 'level': { '$gt': 5 } },{'p_node' : x['customer_id']}]} ).count()
        if int(customers_child1) >= 2  and float(x['total_node']) >= 100000:
            db.users.update({ "customer_id" : x['customer_id'] }, { '$set': { "league": 1 }})

    #League 2
    customers2 = db.users.find({ 'level': { '$gt': 0 } })
    for y in customers2:
        customers_child2 = db.users.find({'$and' :[{ 'league': { '$gt': 0 } },{'p_node' : y['customer_id']}]} ).count()
        if int(customers_child2) >= 2:
            db.users.update({ "customer_id" : y['customer_id'] }, { '$set': { "league": 2 }})

    #League 3
    customers3 = db.users.find({ 'level': { '$gt': 0 } })
    for z in customers3:
        customers_child3 = db.users.find({'$and' :[{ 'league': { '$gt': 1 } },{'p_node' : z['customer_id']}]} ).count()
        if int(customers_child3) >= 2:
            db.users.update({ "customer_id" : z['customer_id'] }, { '$set': { "league": 3 }})

    #League 4
    customers4 = db.users.find({ 'level': { '$gt': 0 } })
    for a in customers4:
        customers_child4 = db.users.find({'$and' :[{ 'league': { '$gt': 2 } },{'p_node' : a['customer_id']}]} ).count()
        if int(customers_child4) >= 2:
            db.users.update({ "customer_id" : a['customer_id'] }, { '$set': { "league": 4 }})

    #League 5
    customers5 = db.users.find({ 'level': { '$gt': 0 } })
    for b in customers5:
        customers_child5 = db.users.find({'$and' :[{ 'league': { '$gt': 3 } },{'p_node' : b['customer_id']}]} ).count()
        if int(customers_child5) >= 2:
            db.users.update({ "customer_id" : b['customer_id'] }, { '$set': { "league": 5 }})

    #League 6
    customers6 = db.users.find({ 'level': { '$gt': 0 } })
    for c in customers6:
        customers_child6 = db.users.find({'$and' :[{ 'league': { '$gt': 4 } },{'p_node' : c['customer_id']}]} ).count()
        if int(customers_child6) >= 2:
            db.users.update({ "customer_id" : c['customer_id'] }, { '$set': { "league": 6 }})

    return True

def Getlevel(customer_id):
    count_f1 = db.users.find({"p_node" : customer_id }).count()
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

    db.users.update({ "customer_id" : customer_id }, { '$set': { "level": level }})
    return level
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

    amount_invest = float(amount_invest)*float(price_currency)

    if customer_ml['p_node'] != '':
        while (True):
            customer_ml_p_node = db.users.find_one({"customer_id" : customer_ml['p_node'] })
            if customer_ml_p_node is None:
                break
            else:
                customers = db.users.find_one({"customer_id" : customer_ml_p_node['customer_id'] })
                customers['total_node'] = float(customers['total_node']) + float(amount_invest)
                db.users.save(customers)
                
            customer_ml = db.users.find_one({"customer_id" : customer_ml_p_node['customer_id'] })
            if customer_ml is None:
                break
    return True