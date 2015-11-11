from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask.ext.redis import FlaskRedis

from models.users import RegistrationForm, LoginForm

import hashlib
import time
import ast
from pprint import PrettyPrinter

application = Flask(__name__)
redis = FlaskRedis(application)

@application.route("/")
def index():
    return render_template('index.html')

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
    else:
        flash('invalid format!')
        return redirect(url_for('register'))
    return redirect(url_for('index'))

@application.route("/home")
def home():
    return render_template('home.html')

@application.route("/pomsg", methods=['POST'])
def pomsg():
    return redirect(url_for('home'))

@application.route("/delmsg/<msgid>", methods=['POST'])
def delmsg():
    return redirect(url_for('home'))

@application.route("/profile")
def profile():
    if not session.get('logged_in'):
        redirect(url_for('index'))
    profile_info = ast.literal_eval(redis.hget('user', session['logged_in']))
    profile_info.pop('password', None)
    profile_info['register time'] = profile_info.pop('regtime')
    return render_template('profile.html', profile_info=profile_info)

@application.route("/logout")
def logout():
    session.pop('logged_in', None)
    flash('logout successfully')
    return redirect(url_for('index'))

if __name__ == "__main__":
    application.secret_key = 'super secret key'
    application.debug = True
    application.run()
