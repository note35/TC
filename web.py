from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask.ext.redis import FlaskRedis

from models.users import RegistrationForm, LoginForm
from models.messages import PostForm 

import hashlib
import time
import ast
from pprint import PrettyPrinter

application = Flask(__name__)
redis = FlaskRedis(application)

@application.route("/")
def index():
    msg_list = redis.lrange('messages', 0, redis.llen('messages'))
    msgs = []
    if msg_list:
        for mid in msg_list:
            msg = ast.literal_eval(redis.hget('message', mid))
            msgs.append(msg)
    return render_template('index.html', msgs=msgs)

@application.route("/login")
def login():
    form = LoginForm()
    if session.get('logged_in'):
        redirect(url_for('home'))
    return render_template('login.html', form=form) 

@application.route("/verify_login", methods=['POST'])
def verify_login():
    form = LoginForm(request.form)
    if session.get('logged_in'):
        redirect(url_for('home')) 
    elif request.method == 'POST' and form.validate():
        if redis.hget('user', form.username.data):
            login_user = ast.literal_eval(redis.hget('user', form.username.data)) 
            if login_user['password'] == hashlib.sha224(form.password.data).hexdigest():
                flash('login successfully!')
                session['logged_in'] = form.username.data
                return redirect(url_for('home'))
            #debug backdoor
            elif form.username.data == 'admin' and form.password.data == '12345':
                flash('login successfully!')
                session['logged_in'] = form.username.data
                return redirect(url_for('home'))
            else:
                flash('wrong password!')                 
        else:
            flash('no such user!')
    return redirect(url_for('login')) 

@application.route("/register")
def register():
    #debug
    #pp = PrettyPrinter()
    #print redis.lrange('users', 0, redis.llen('users'))
    #pp.pprint(redis.hgetall('user'))
    form = RegistrationForm()
    if session.get('logged_in'):
        redirect(url_for('home'))
    return render_template('register.html', form=form)

@application.route("/verify_register", methods=['POST'])
def verify_register():
    form = RegistrationForm(request.form)
    if session.get('logged_in'):
        redirect(url_for('home'))
    if request.method == 'POST' and form.validate():
      try:
        if redis.hget('user', form.username.data) == None:
            if form.password.data == form.confirm_password.data:
                if redis.lrange('users', 0, 1):
                    ori_last_uid = int(redis.lrange('users', 0, 1)[0])
                else:
                    ori_last_uid = 0
                redis.lpush('users', str(ori_last_uid+1))
                redis.hset('user', form.username.data, 
                    {   'uid':ori_last_uid+1,
                        'username':form.username.data,
                        'password':hashlib.sha224(form.password.data).hexdigest(),
                        'regtime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) })
                flash('register successfully!')
                session['logged_in'] = form.username.data
                return redirect(url_for('home'))
            else:
                flash('password is not equal to confirm password, try again!')
                return redirect(url_for('register'))
        else:
            flash('username is be used!')
            return redirect(url_for('register'))
      except Exception, e:
        print str(e.args)

    else:
        flash('invalid format!')
        return redirect(url_for('register'))
    return redirect(url_for('index'))

@application.route("/home")
def home():
    if not session.get('logged_in'):
        redirect(url_for('index'))
    form = PostForm()
    msg_list_by_id = redis.lrange('messages:'+session['logged_in'], 0, redis.llen('messages:'+session['logged_in']))
    msgs = []
    if msg_list_by_id:
        for mid in msg_list_by_id:
            msg = ast.literal_eval(redis.hget('message', mid))
            msgs.append(msg)
    return render_template('home.html', form=form, msgs=msgs)

@application.route("/pomsg", methods=['POST'])
def pomsg():
    if not session.get('logged_in'):
        redirect(url_for('index'))
    form = PostForm(request.form)
    if request.method == 'POST' and form.validate():
        if redis.lrange('messages', 0, 1):
            ori_last_mid = int(redis.lrange('messages', 0, 1)[0])
        else:
            ori_last_mid = 0

        redis.lpush('messages', str(ori_last_mid+1))
        redis.lpush('messages:'+session['logged_in'], str(ori_last_mid+1))
        redis.hset('message', str(ori_last_mid+1), 
             {  'mid': str(ori_last_mid+1),
                'time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
                'user': session['logged_in'],   
                'message': form.message.data })
    return redirect(url_for('home'))

@application.route("/delmsg/<msg_id>", methods=['GET'])
def delmsg(msg_id):
    if not session.get('logged_in'):
        redirect(url_for('index')) 
    if request.method == 'GET':
        if ast.literal_eval(redis.hget('message', msg_id))['user'] == session['logged_in']:
            redis.hdel('message', msg_id)
            redis.lrem('messages', msg_id)
            redis.lrem('messages:'+session['logged_in'], msg_id)
    flash ('delete messages ' + msg_id + ' successfully!')
    return redirect(url_for('home'))

@application.route("/profile")
def profile():
    if not session.get('logged_in'):
        redirect(url_for('index'))
    profile_info = ast.literal_eval(redis.hget('user', session['logged_in']))
    profile_info.pop('password', None)
    return render_template('profile.html', profile_info=profile_info)

@application.route("/logout")
def logout():
    session.pop('logged_in', None)
    flash('logout successfully!')
    return redirect(url_for('index'))

if __name__ == "__main__":
    application.secret_key = 'super secret key'
    application.config['SESSION_TYPE'] = 'filesystem'
    application.debug = True
    application.run()
