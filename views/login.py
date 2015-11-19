from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from models.users import LoginForm

from decorator import login_not_required

from lib.database import db
from lib import form

from oauth2client.client import flow_from_clientsecrets
from apiclient import discovery
import httplib2
import hashlib
import time

database = db()
database.init_db()

login_blueprint = Blueprint('login', __name__, template_folder='templates', static_folder='static')

def create_flow():
    return flow_from_clientsecrets('client_secret.json', scope='openid profile',
                                   redirect_uri=url_for('login.oauth2cb', _external=True))

def flow_step_1():
    flow = create_flow()
    return flow.step1_get_authorize_url()

def flow_step_2(callback_code):
    flow = create_flow()
    if callback_code:
        credentials = flow.step2_exchange(callback_code)
        http_auth = credentials.authorize(httplib2.Http())
        profile = discovery.build('oauth2', 'v2', http_auth)
        user_info = profile.userinfo().get().execute()
        return user_info['id'], user_info['given_name'], user_info['picture']

@login_blueprint.route("/google_login")
def google_login():
    auth_uri = flow_step_1()
    return redirect(auth_uri)

@login_blueprint.route("/oauth2cb")
def oauth2cb():
    if 'code' in request.args:
        goog_user_id, user_given_name, goog_user_avatar = flow_step_2(request.args['code'])
        # if you haven't login, add user
        if database.get_user_by_username('google:'+goog_user_id+':'+user_given_name) == None:
            ori_last_uid = database.get_latest_uid()
            username = 'google:'+goog_user_id+':'+user_given_name
            user_info = { 'uid':ori_last_uid+1,
                         'goog_user_id':goog_user_id,
                         'goog_user_avatar': goog_user_avatar,
                         'username':user_given_name,
                         'regtime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) }
            database.add_user(str(ori_last_uid+1), username, user_info)
        flash('login successfully!')
        session['logged_in'] = 'google:'+goog_user_id+':'+user_given_name 
        session['avatar'] = goog_user_avatar
        return redirect(url_for('home.home'))
    else:
        flash('google login failed!')
        return redirect(url_for('index.index'))

@login_blueprint.route("/login")
@login_not_required
def login():
    form = LoginForm()
    return render_template('login.html', form=form) 

@login_blueprint.route("/verify_login", methods=['POST'])
@login_not_required
def verify_login():
    loginform = LoginForm(request.form)
    if request.method == 'POST' and loginform.validate():
        if database.get_user_by_username(loginform.username.data):
            login_user = database.get_user_by_username(loginform.username.data)
            if login_user['password'] == hashlib.sha224(loginform.password.data).hexdigest():
                flash('login successfully!')
                session['logged_in'] = loginform.username.data
                return redirect(url_for('home.home'))
            else:
                flash('wrong password!')                 
        else:
            flash('no such user!')
    elif request.method == 'POST' and not loginform.validate():
        form.flash_errors(loginform) 
    return redirect(url_for('login.login')) 

@login_blueprint.route("/logout")
def logout():
    session.clear()
    flash('logout successfully!')
    return redirect(url_for('index.index'))
