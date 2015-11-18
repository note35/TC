from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from models.messages import PostForm 

from decorator import login_required

from lib import s3
from lib.database import db
from lib import form
from lib import pagination

from werkzeug.utils import secure_filename
import time
import json

database = db()
database.init_db()

home_blueprint = Blueprint('home', __name__, template_folder='templates', static_folder='static')
msgs_in_each_page = pagination.msgs_in_each_page
 
@home_blueprint.route("/home/")
@home_blueprint.route("/home")
@login_required
def home():
    postform = PostForm()
    total_pages = len(database.get_msg_list())/msgs_in_each_page+1
    return render_template('home.html', form=postform, total_pages=total_pages)

@home_blueprint.route("/home/<request_page>")
@login_required
def page(request_page):
    message_list_by_id = pagination.get_page(request_page, session['logged_in'])

    if 'error' in message_list_by_id:
        flash(str(request_page)+' page is not exist')
        return render_template('404.html')

    messages = []
    if message_list_by_id:
        for mid in message_list_by_id:
            message = database.get_msg_by_id(mid)
            if message['user'].split(':')[0] == 'google':
                message['user'] = message['user'].split(':')[2]
            messages.append(message)
            if 'image' in message:
                message['image_data'] = s3.s3_get(message['image'])
    return json.dumps(messages) 

@home_blueprint.route("/pomsg", methods=['POST'])
@login_required
def pomsg():
    postform = PostForm(request.form)
    if request.method == 'POST' and postform.validate():
        ori_last_mid = database.get_latest_mid()
        message ={  'mid': str(ori_last_mid+1),
                    'time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
                    'user': session['logged_in'], 
                    'message': postform.message.data }
        image = request.files[postform.upload.name]
        if image:
            if image.content_type.startswith('image/'):
                filename = session['logged_in'] + ':' + str(ori_last_mid+1) + ':' + secure_filename(image.filename)
                s3.s3_put(filename, image)
                message['image'] = filename
            else:
                flash("upload file error, due to wrong file-content")
                return redirect(url_for('home.home'))
        database.add_msg(str(ori_last_mid+1), session['logged_in'], message)
    elif request.method == 'POST' and not postform.validate():
        form.flash_errors(postform)
    return redirect(url_for('home.home'))

@home_blueprint.route("/delmsg/<mid>", methods=['GET'])
@login_required
def delmsg(mid):
    if request.method == 'GET':
        message = database.get_msg_by_id(mid)
        if message['user'] == session['logged_in']:
            if 'image' in message:
                s3.s3_delete(message['image'])
            database.del_msg(mid, session['logged_in'])
    flash ('delete messages successfully!')
    return redirect(url_for('home.home'))

