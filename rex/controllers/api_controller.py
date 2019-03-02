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


__author__ = 'asdasd'

api_ctrl = Blueprint('api', __name__, static_folder='static', template_folder='templates')
UPLOAD_FOLDER = '/statics/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])



def id_generator(size=6, chars=string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
def to_bytes(n, length):
    s = '%x' % n
    s = s.rjust(length*2, '0')
    s = codecs.decode(s.encode("UTF-8"), 'hex_codec')
    return s

def decode_base58(bc, length):
    n = 0
    for char in bc:
        n = n * 58 + digits58.index(char)
    return to_bytes(n, length)

def check_bc(bc):
    bcbytes = decode_base58(bc, 25)
    return bcbytes[-4:] == sha256(sha256(bcbytes[:-4]).digest()).digest()[:4]

def check_password(pw_hash, password):
        return check_password_hash(pw_hash, password)

def set_password(password):
    return generate_password_hash(password)

@api_ctrl.route('/register', methods=['GET', 'POST'])
def register():
    dataDict = json.loads(request.data)
    email = dataDict['email'].lower()
    password = dataDict['password'].lower()
    p_node = dataDict['p_node'].lower()
    
    check_email = db.User.find_one({'email': email})
    if check_email is not None and email != '':
      return json.dumps({
          'status': 'error', 
          'message': 'Email has been used. Please use another email account' 
      })
    else:
      create_account(email,password,p_node)
      #sendmail forgot password
      return json.dumps({
          'status': 'complete', 
          'message': 'Account successfully created' 
      })

@api_ctrl.route('/login', methods=['GET', 'POST'])
def login():
   
    dataDict = json.loads(request.data)
    email = dataDict['email'].lower()
    password = dataDict['password'].lower()
      
    user = db.User.find_one({'email': email})

    if user is None or check_password(user['password'], password) == False:
        return json.dumps({
          'status': 'error', 
          'message': 'Invalid login information. Please try again' 
      })
    else:
        if int (user['active_email']) == 1: 
          return json.dumps({
            'customer_id' : user['customer_id'],
            'status': 'complete', 
            'message': 'Login successfully' 
          })
        else:
          return json.dumps({
            'status': 'error', 
            'message': 'Account has not been activated yet' 
          })  



@api_ctrl.route('/change-password', methods=['GET', 'POST'])
def change_password():
   
    dataDict = json.loads(request.data)
    password_old = dataDict['password_old'].lower()
    password_new = dataDict['password_new'].lower()
    customer_id = dataDict['customer_id'].lower()

    user = db.User.find_one({'customer_id': customer_id})

    if user is None:
        return json.dumps({
          'status': 'error', 
          'message': 'Email does not exist. Please try again' 
      })
    else:
        if check_password(user['password'], password_old) == False:
        
          return json.dumps({
            'status': 'error', 
            'message': 'Old password is not correct' 
          })
        else:
          db.users.update({ "customer_id" : customer_id }, { '$set': { "password": set_password(password_new) }})
          return json.dumps({
            'status': 'complete', 
            'message': 'Change password successfully' 
          })  

@api_ctrl.route('/update-img-profile', methods=['GET', 'POST'])
def update_img_profile():
   
    dataDict = json.loads(request.data)
    base64Image = dataDict['base64Image']
    customer_id = dataDict['customer_id'].lower()

    db.users.update({ "customer_id" : customer_id }, { '$set': { "img_profile": base64Image }})
    return json.dumps({
      'status': 'complete'
    }) 
    

@api_ctrl.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
   
    dataDict = json.loads(request.data)
    email = dataDict['email'].lower()
     
    user = db.User.find_one({'email': email})

    if user is None:
        return json.dumps({
          'status': 'error', 
          'message': 'Email does not exist. Please try again' 
      })
    else:
        if int (user['active_email']) == 1:
          #sendmail forgot password 
          return json.dumps({
            'status': 'complete', 
            'message': 'Forgot Password successfully' 
          })
        else:
          return json.dumps({
            'status': 'error', 
            'message': 'Account has not been activated yet' 
          })  

@api_ctrl.route('/resend-code', methods=['GET', 'POST'])
def resend_code():
   
    dataDict = json.loads(request.data)
    email = dataDict['email'].lower()
     
    user = db.User.find_one({'email': email})

    if user is None:
        return json.dumps({
          'status': 'error', 
          'message': 'Email does not exist. Please try again' 
      })
    else:
        if int (user['active_email']) != 1:
          

          code_active = id_generator()
          print code_active
          db.users.update({"email": email}, { "$set": { "code_active":code_active} })
          #sendmail Resend Code
          return json.dumps({
            'status': 'complete', 
            'message': 'Resend Code successfully' 
          })
        else:
          return json.dumps({
            'status': 'error', 
            'message': 'Account has been activated' 
          })  

@api_ctrl.route('/active-code', methods=['GET', 'POST'])
def active_code():

    time.sleep(1)
    dataDict = json.loads(request.data)
    email = dataDict['email'].lower()
    code = dataDict['code'].lower()
    
    check_email = db.User.find_one({'email': email})
    if check_email is not None:
      if check_email.code_active != code:
        return json.dumps({
            'status': '', 
            'message': 'The code you entered is incorrect. Please try again.' 
        })
      else:
        db.users.update({"email": email}, { "$set": { "active_email":1} })
        return json.dumps({
            'status': 'complete', 
            'customer_id' : check_email['customer_id'],
            'message': 'The account has been successfully activated.' 
        })
    else:
      return json.dumps({
          'status': 'error', 
          'message': 'Error Network.' 
      })

@api_ctrl.route('/get-version-app', methods=['GET', 'POST'])
def get_version_app():
    return json.dumps({
        'status': 'complete', 
        'version': '1' 
    })


def create_account(email,password,p_node):
    localtime = time.localtime(time.time())
    customer_id = '%s%s%s%s%s%s'%(localtime.tm_mon,localtime.tm_year,localtime.tm_mday,localtime.tm_hour,localtime.tm_min,localtime.tm_sec)
    code_active = id_generator()
    print code_active
    datas = {
        'customer_id' : customer_id,
        'username': email,
        'password': set_password(password),
        'email': email,
        'p_node': p_node,
        'p_binary': '',
        'left': '',
        'right': '',
        'level': 1,
        'telephone' : '',
        'position': '',
        'creation': datetime.utcnow(),
        'total_pd_left' : 0,
        'total_pd_right' : 0,
        'm_wallet' : 0,
        'r_wallet' : 0,
        's_wallet' : 0,
        'max_out' : 0,
        'total_earn' : 0,
        'img_profile' :'/assets/imgs/logo.png',
        'total_invest': 0,
        'btc_address' : '',
        'eth_address' : '',
        'ltc_address' : '',
        'xrp_address' : '',
        'usdt_address' : '',
        'coin_address' : '',

        'status' : 0,
        'type': 0,
        'code_active' : code_active,
        'btc_balance': 0,
        'eth_balance': 0,
        'xrp_balance': 0,
        'ltc_balance': 0,
        'usdt_balance': 0,
        'coin_balance': 0,
        'total_max_out': 0,
        'total_capital_back': 0,
        'total_commission': 0,
        'secret_2fa':'',
        'status_2fa': 0,
        'status_withdraw' : 0,
        'investment' : 0,
        'active_email' : 0
    }
    customer = db.users.insert(datas)
    return True

def send_mail_register(email,usernames,link_active):
    html = """\
        <div style="font-family:Arial,sans-serif;background-color:#f9f9f9;color:#424242;text-align:center">
       <div class="adM">
       </div>
       <table style="table-layout:fixed;width:90%;max-width:600px;margin:0 auto;background-color:#f9f9f9">
          <tbody>
             <tr>
                <td style="padding:20px 10px 10px 0px;text-align:left">
                   <a href="https://worldtrader.info" title="World Trade" target="_blank" >
                   <img src="https://worldtrader.info/static/home/images/logo/logo.png" alt="World Trade" class="CToWUd" style=" width: 200px; ">
                   </a>
                </td>
                <td style="padding:0px 0px 0px 10px;text-align:right">
                </td>
             </tr>
          </tbody>
       </table>
    </div>
    <div style="font-family:Arial,sans-serif;background-color:#f9f9f9;color:#424242;text-align:center">
       <table style="table-layout:fixed;width:90%;max-width:600px;margin:0 auto;background:#fff;font-size:14px;border:2px solid #e8e8e8;text-align:left;table-layout:fixed">
          <tbody>
             <tr>
                <td style="padding:30px 30px 10px 30px;line-height:1.8">Dear <b>"""+str(usernames)+"""</b>,</td>
             </tr>
             <tr>
                <td style="padding:10px 30px;line-height:1.8">Thank you for registering on the <a href="https://worldtrader.info/" target="_blank">World Trade</a>.</td>
             </tr>
             <tr>
                <td style="padding:10px 30px;line-height:1.8">Your World Trade verification code is: <b>"""+str(link_active)+"""</b></td>
             </tr>

             <tr>
                <td style="border-bottom:3px solid #efefef;width:90%;display:block;margin:0 auto;padding-top:30px"></td>
             </tr>
             <tr>
                <td style="padding:30px 30px 30px 30px;line-height:1.3">Best regards,<br> <a href="https://worldtrader.info/" target="_blank" >World Trade</a></td>
             </tr>
          </tbody>
       </table>
    </div>
    <div style="font-family:Arial,sans-serif;background-color:#f9f9f9;color:#424242;text-align:center;padding-bottom:10px;     height: 50px;">
   
</div>
    """

    return requests.post(
      "https://api.mailgun.net/v3/worldtrader.info/messages",
      auth=("api", "key-4cba65a7b1a835ac14b7949d5795236a"),
      data={"from": "World Trade <no-reply@worldtrader.info>",
        "to": ["", email],
        "subject": "Account registration successful",
        "html": html})


   