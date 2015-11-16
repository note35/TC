from flask import Blueprint, Flask, render_template, request, redirect, url_for, session, flash
from flask.ext.redis import FlaskRedis

from models.users import RegistrationForm, LoginForm
from models.messages import PostForm 

from decorator import login_required, login_not_required
#from views.index import index_blueprint

from lib import s3#, db_cmd

from werkzeug.utils import secure_filename
from oauth2client.client import flow_from_clientsecrets
from apiclient import discovery
import httplib2
import hashlib
import time
import ast

application = Flask(__name__)
#db = db_cmd(application)
redis = FlaskRedis(application)

#application.register_blueprint(index_blueprint)
@application.route('/')
def index():
    message_list = redis.lrange('messages', 0, redis.llen('messages'))
    messages = []
    if message_list:
        for mid in message_list:
            message = ast.literal_eval(redis.hget('message', mid))
            if message['user'].split(':')[0] == 'google':
                message['user'] = message['user'].split(':')[2] 
            if 'image' in message:
                message['image_data'] = s3.s3_get(message['image'])
            messages.append(message)
    return render_template('index.html', msgs=messages)

def create_flow():
    return flow_from_clientsecrets('static/client_secret.json', scope='openid profile',
                                   redirect_uri=url_for('oauth2cb', _external=True))

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
        print user_info
        return user_info['id'], user_info['given_name'], user_info['picture']

@application.route("/google_login")
def google_login():
    auth_uri = flow_step_1()
    return redirect(auth_uri)

@application.route("/oauth2cb")
def oauth2cb():
    if 'code' in request.args:
        goog_user_id, user_given_name, goog_user_avatar = flow_step_2(request.args['code'])
        # if you haven't login, add user
        if redis.hget('user', 'google:'+goog_user_id+':'+user_given_name) == None:
            if redis.lrange('users', 0, 1):
                ori_last_uid = int(redis.lrange('users', 0, 1)[0])
            else:
                ori_last_uid = 0
            redis.lpush('users', str(ori_last_uid+1))
            redis.hset('user', 'google:'+goog_user_id+':'+user_given_name, 
                {   'uid':ori_last_uid+1,
                    'goog_user_id':goog_user_id,
                    'goog_user_avatar': goog_user_avatar,
                    'username':user_given_name,
                    'regtime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) })
        flash('login successfully!')
        session['logged_in'] = 'google:'+goog_user_id+':'+user_given_name 
        session['avatar'] = goog_user_avatar
        return redirect(url_for('home'))
    else:
        flash('google login failed!')
        return redirect(url_for('index'))

@application.route("/login")
@login_not_required
def login():
    form = LoginForm()
    return render_template('login.html', form=form) 

@application.route("/verify_login", methods=['POST'])
@login_not_required
def verify_login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        if redis.hget('user', form.username.data):
            login_user = ast.literal_eval(redis.hget('user', form.username.data)) 
            if login_user['password'] == hashlib.sha224(form.password.data).hexdigest():
                flash('login successfully!')
                session['logged_in'] = form.username.data
                return redirect(url_for('home'))
            else:
                flash('wrong password!')                 
        else:
            flash('no such user!')
    elif request.method == 'POST' and not form.validate():
        flash_errors(form) 
    return redirect(url_for('login')) 

@application.route("/register")
@login_not_required
def register():
    form = RegistrationForm()
    return render_template('register.html', form=form)

@application.route("/verify_register", methods=['POST'])
@login_not_required
def verify_register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate() and ':' not in form.username.data:
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
@login_required
def home():
    form = PostForm()
    message_list_by_id = redis.lrange('messages:'+session['logged_in'], 0, redis.llen('messages:'+session['logged_in']))
    messages = []
    if message_list_by_id:
        for mid in message_list_by_id:
            message = ast.literal_eval(redis.hget('message', mid))
            if message['user'].split(':')[0] == 'google':
                message['user'] = message['user'].split(':')[2]
            messages.append(message)
            if 'image' in message:
                message['image_data'] = s3.s3_get(message['image'])
    return render_template('home.html', form=form, msgs=messages)

@application.route("/pomsg", methods=['POST'])
@login_required
def pomsg():
    form = PostForm(request.form)
    if request.method == 'POST' and form.validate():
        if redis.lrange('messages', 0, 1):
            ori_last_mid = int(redis.lrange('messages', 0, 1)[0])
        else:
            ori_last_mid = 0
        message ={  'mid': str(ori_last_mid+1),
                    'time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
                    'user': session['logged_in'], 
                    'message': form.message.data }
        image = request.files[form.upload.name]
        if image:
            filename = session['logged_in'] + ':' + str(ori_last_mid+1) + ':' + secure_filename(image.filename)
            s3.s3_put(filename, image)
            message['image'] = filename

        redis.lpush('messages', str(ori_last_mid+1))
        redis.lpush('messages:'+session['logged_in'], str(ori_last_mid+1))
        redis.hset('message', str(ori_last_mid+1), message) 

    elif request.method == 'POST' and not form.validate():
        flash_errors(form)
    return redirect(url_for('home'))

@application.route("/delmsg/<mid>", methods=['GET'])
@login_required
def delmsg(mid):
    if request.method == 'GET':
        message = ast.literal_eval(redis.hget('message', mid))
        if message['user'] == session['logged_in']:
            if 'image' in message:
                s3.s3_delete(msg['image'])
            redis.hdel('message', mid)
            redis.lrem('messages', mid)
            redis.lrem('messages:'+session['logged_in'], mid)

    flash ('delete messages successfully!')
    return redirect(url_for('home'))

'''
@application.route('/profile<regex(".json"):ext')
def profile():
    if not session.get('logged_in'):
        redirect(url_for('index'))
    profile_info = ast.literal_eval(redis.hget('user', session['logged_in']))
    profile_info.pop('password', None)
    if ext == '.json':
       return json.dumps(profile_info)
    return render_template('profile.html', profile_info=profile_info)
'''

@application.route('/profile')
@login_required
def profile():
    profile_info = ast.literal_eval(redis.hget('user', session['logged_in']))
    profile_info.pop('password', None)
    return render_template('profile.html', profile_info=profile_info)

@application.route("/logout")
def logout():
    session.clear()
    flash('logout successfully!')
    return redirect(url_for('index'))

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))

if __name__ == "__main__":
    application.secret_key = 'super secret key'
    application.config['SESSION_TYPE'] = 'filesystem'
    application.debug = True
    application.run(host='0.0.0.0', port=8080)
    #application.run(host='52.192.157.72', port=443)
