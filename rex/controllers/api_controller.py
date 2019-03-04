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
      customer_id = create_account(email,password,p_node)

      return json.dumps({
          'status': 'complete', 
          'customer_id' : customer_id,
          'message': 'Account successfully created' 
      })
# @api_ctrl.route('/testmail', methods=['GET', 'POST'])
# def testmail():
#     sendmail_forgot_password('trungdoanict@gmail.com','1313123')
#     return json.dumps({
#         'status': 'complete' 
        
#     })
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
            'customer_id' : user['customer_id'],
            'status': 'error_active_email', 
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

@api_ctrl.route('/update-infomation', methods=['GET', 'POST'])
def update_infomation():
   
    dataDict = json.loads(request.data)
    first_name = dataDict['first_name']
    last_name = dataDict['last_name']
    birth_day = dataDict['birth_day']
    address = dataDict['address']
    telephone = dataDict['telephone']
    customer_id = dataDict['customer_id'].lower()

    user = db.User.find_one({'customer_id': customer_id})

    if user is None:
        return json.dumps({
          'status': 'error', 
          'message': 'Error' 
      })
    else:
        user['personal_info']['firstname'] = first_name
        user['personal_info']['lastname'] = last_name
        user['personal_info']['date_birthday'] = birth_day
        user['personal_info']['address'] = address
        user['telephone'] = telephone
        db.users.save(user)
        return json.dumps({
          'status': 'complete', 
          'message': 'Update account information successfully' 
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
          password = id_generator(6)
          password_new = set_password(password)
          db.users.update({ "_id" : ObjectId(user['_id']) }, { '$set': {'password': password_new } })
          sendmail_forgot_password(email,password) 
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
    customer_id = dataDict['customer_id'].lower()
     
    user = db.User.find_one({'customer_id': customer_id})

    if user is None:
        return json.dumps({
          'status': 'error', 
          'message': 'Please try again' 
      })
    else:
        if int (user['active_email']) != 1:
          
          # code_active = id_generator()
          # print code_active
          # db.users.update({"customer_id": customer_id}, { "$set": { "code_active":code_active} })
          #sendmail Resend Code user['code_active']

          send_mail_register(user['code_active'],user['email'])
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
    customer_id = dataDict['customer_id'].lower()
    code = dataDict['code'].lower()
    
    check_email = db.User.find_one({'customer_id': customer_id})
    if check_email is not None:
      if check_email.code_active != code:
        return json.dumps({
            'status': '', 
            'message': 'The code you entered is incorrect. Please try again.' 
        })
      else:
        db.users.update({"customer_id": customer_id}, { "$set": { "active_email":1} })
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


@api_ctrl.route('/upload-img-profile/<customer_id>', methods=['GET', 'POST'])
def upload_img_profile(customer_id):
    
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    
    upload     = request.files.get('file')
    
    save_path = SITE_ROOT+'/../static/img/upload'.format(category='category')
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    name = upload.filename
    file_path = "{path}/{file}".format(path=save_path, file=name)
    upload.save(file_path)
    
    url_img_save = 'https://api.buy-sellpro.co/static/img/upload/'+name
    print url_img_save
    db.users.update({ "customer_id" : customer_id }, { '$set': { "img_profile": url_img_save } })
    return json.dumps({
        'status': 'complete', 
        'name_ifle' : url_img_save
    })
    
@api_ctrl.route('/upload-img-passport-fontside/<customer_id>', methods=['GET', 'POST'])
def upload_img_passport_fontside(customer_id):
    
    print customer_id
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    
    upload     = request.files.get('file')
    
    save_path = SITE_ROOT+'/../static/img/upload'.format(category='category')
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    name = upload.filename
    file_path = "{path}/{file}".format(path=save_path, file=name)
    upload.save(file_path)
    
    url_img_save = 'https://api.buy-sellpro.co/static/img/upload/'+name
    print url_img_save

    user = db.users.find_one({'customer_id': customer_id})
    user['personal_info']['img_passport_fontside'] = url_img_save
    db.users.save(user)
    return json.dumps({
        'status': 'complete'
    })

@api_ctrl.route('/upload-img-passport-backside/<customer_id>', methods=['GET', 'POST'])
def upload_img_passport_backside(customer_id):
    
    print customer_id
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    
    upload     = request.files.get('file')
    
    save_path = SITE_ROOT+'/../static/img/upload'.format(category='category')
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    name = upload.filename
    file_path = "{path}/{file}".format(path=save_path, file=name)
    upload.save(file_path)
    
    url_img_save = 'https://api.buy-sellpro.co/static/img/upload/'+name
    print url_img_save

    user = db.users.find_one({'customer_id': customer_id})
    user['personal_info']['img_passport_backside'] = url_img_save
    db.users.save(user)
    return json.dumps({
        'status': 'complete'
    })
    
@api_ctrl.route('/upload-img-address/<customer_id>', methods=['GET', 'POST'])
def upload_img_address(customer_id):
    
    print customer_id
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    
    upload     = request.files.get('file')
    
    save_path = SITE_ROOT+'/../static/img/upload'.format(category='category')
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    name = upload.filename
    file_path = "{path}/{file}".format(path=save_path, file=name)
    upload.save(file_path)
    
    url_img_save = 'https://api.buy-sellpro.co/static/img/upload/'+name
    print url_img_save

    user = db.users.find_one({'customer_id': customer_id})
    user['personal_info']['img_address'] = url_img_save
    db.users.save(user)
    return json.dumps({
        'status': 'complete'
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
        'level': 0,
        'telephone' : '',
        'position': '',
        'creation': datetime.utcnow(),
        'total_pd_left' : 0,
        'total_pd_right' : 0,
        'd_wallet' : 0,#Profit day
        'r_wallet' : 0,#Direct commission
        's_wallet' : 0,#System commission
        'l_wallet' : 0,#Leadership commission
        'ss_wallet' : 0,#Share sales
        'sf_wallet' : 0,#Share Fund
        'max_out' : 0,
        'total_earn' : 0,
        'img_profile' :'assets/imgs/logo.png',
        'total_invest': 0,
        'btc_address' : '',
        'eth_address' : '',
        'ltc_address' : '',
        'xrp_address' : '',
        'usdt_address' : '',
        'coin_address' : '',
        'total_node' : 0,
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
        'active_email' : 0,
        'verification' : 0,
        'personal_info' : { 
        'firstname' : '',
        'lastname' : '',
        'date_birthday' :'',
        'address' :'',
        'postalcode' : '',
        'city' : '',
        'country' : '',
        'img_passport_fontside' : '',
        'img_passport_backside' : '',
        'img_address' : ''
      } 
    }
    customer = db.users.insert(datas)
    send_mail_register(code_active,email)
    return customer_id


def send_mail_register(code_active,email):
    html = """ 
      <div style="width: 100%; "><div style="background: #2E6F9C; height: 150px;text-align: center;"><img src="https://i.ibb.co/tH5J6C2/logo.png" width="120px;" style="margin-top: 30px;" /></div><br><br>
      Thank you for registering with Asipay. Please enter the code to activate the account.<br><br>
      Your code is: <b>"""+str(code_active)+"""</b>
      <br><br><br>Regards,<br>Asipay Account Services<div class="yj6qo"></div><div class="adL"><br><br><br></div></div>
    """
    return requests.post(
      "https://api.mailgun.net/v3/diamondcapital.co/messages",
      auth=("api", "key-cade8d5a3d4f7fcc9a15562aaec55034"),
      data={"from": "Asipay <info@diamondcapital.co>",
        "to": ["", email],
        "subject": "Account registration successful",
        "html": html}) 
    return True

   
def sendmail_forgot_password(email,password):
    html = """ 
      <div style="width: 100%; "><div style="background: #2E6F9C; height: 150px;text-align: center;"><img src="https://i.ibb.co/tH5J6C2/logo.png" width="120px;" style="margin-top: 30px;" /></div><br><br>
      Thank you for registering with Asipay. Please enter a new password to login.<br><br>
      Your password new is: <b>"""+str(password)+"""</b>
      <br><br><br>Regards,<br>Asipay Account Services<div class="yj6qo"></div><div class="adL"><br><br><br></div></div>
    """
    return requests.post(
      "https://api.mailgun.net/v3/diamondcapital.co/messages",
      auth=("api", "key-cade8d5a3d4f7fcc9a15562aaec55034"),
      data={"from": "Asipay <info@diamondcapital.co>",
        "to": ["", email],
        "subject": "New Password",
        "html": html}) 
    return True

