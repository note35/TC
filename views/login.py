from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import hashlib
import time
import ConfigParser

from models.users import LoginForm
from decorator import login_not_required
from lib.database import db
from lib import form
from lib import google_openid

flash_config = ConfigParser.ConfigParser()
flash_config.read('config/flash.cfg')

database = db()
database.init_db()

login_blueprint = Blueprint('login', __name__, template_folder='templates', static_folder='static')

@login_blueprint.route("/google_login")
def google_login():
    auth_uri = google_openid.flow_step_1()
    return redirect(auth_uri)

@login_blueprint.route("/oauth2cb")
def oauth2cb():
    if 'code' in request.args:
        goog_user_id, user_given_name, goog_user_avatar = google_openid.flow_step_2(request.args['code'])
        if goog_user_id == user_given_name == goog_user_avatar == 'fail':
            flash(flash_config.get('login', 'openid_error'))
            return redirect(url_for('login.login'))
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
        flash(flash_config.get('login', 'login_success'))
        session['logged_in'] = 'google:'+goog_user_id+':'+user_given_name 
        session['avatar'] = goog_user_avatar
        return redirect(url_for('home.home'))
    else:
        flash(flash_config.get('login', 'login_fail'))
        return redirect(url_for('login.login'))

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
                flash(flash_config.get('login', 'login_success'))
                session['logged_in'] = loginform.username.data
                return redirect(url_for('home.home'))
            else:
                flash(flash_config.get('login', 'wrong_password'))
        else:
            flash(flash_config.get('login', 'no_such_user'))
    elif request.method == 'POST' and not loginform.validate():
        form.flash_errors(loginform) 
    return redirect(url_for('login.login')) 

@login_blueprint.route("/logout")
def logout():
    session.clear()
    flash(flash_config.get('login', 'logout_success'))
    return redirect(url_for('index.index'))
