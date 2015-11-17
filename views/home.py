from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from models.messages import PostForm 

from decorator import login_required

from lib import s3
from lib.database import db

from werkzeug.utils import secure_filename
import time
import ast

database = db()
database.init_db()
redis = database.get_db()

home_blueprint = Blueprint('home', __name__, template_folder='templates', static_folder='static')

@home_blueprint.route("/home")
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

@home_blueprint.route("/pomsg", methods=['POST'])
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
    return redirect(url_for('home.home'))

@home_blueprint.route("/delmsg/<mid>", methods=['GET'])
@login_required
def delmsg(mid):
    if request.method == 'GET':
        message = ast.literal_eval(redis.hget('message', mid))
        if message['user'] == session['logged_in']:
            if 'image' in message:
                s3.s3_delete(message['image'])
            redis.hdel('message', mid)
            redis.lrem('messages', mid)
            redis.lrem('messages:'+session['logged_in'], mid)

    flash ('delete messages successfully!')
    return redirect(url_for('home.home'))

