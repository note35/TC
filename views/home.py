from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app, abort
from werkzeug.utils import secure_filename
import time
import json
import ConfigParser
from StringIO import StringIO
import os 
import random

from models.messages import PostForm 
from decorator import login_required
from lib import s3
from lib.database import db
from lib import form
from lib import pagination

flash_config = ConfigParser.ConfigParser()
flash_config.read('config/flash.cfg')

database = db()
database.init_db()

home_blueprint = Blueprint('home', __name__, template_folder='templates', static_folder='static')
msgs_in_each_page = pagination.msgs_in_each_page


html_escape_table = {
     "&": "&amp;",
     '"': "&quot;",
     "'": "&apos;",
     ">": "&gt;",
     "<": "&lt;",
     }

def html_escape(text):
     return "".join(html_escape_table.get(c,c) for c in text)


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
    try:
        message_list_by_id = pagination.get_page(request_page, session['logged_in'])
    except ValueError as ex:
        current_app.logger.error('request_page is not number')
        abort(404)

    if 'error' in message_list_by_id:
        flash(flash_config.get('home', 'page_not_exist'))
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
                    'message': html_escape(postform.message.data) }
        if request.files[postform.upload.name]:
            image = request.files[postform.upload.name]
            tmpfile_name = str(random.randint(1000,9999))+(str(time.strftime('_%H_%M_%S', time.localtime(time.time()))))
            image.save('/tmp/'+tmpfile_name)
            file_length = os.stat('/tmp/'+tmpfile_name).st_size
            if file_length > 4 * 1024 * 1024:
                current_app.logger.warn(str(session['logged_in'])+' upload file too big')
                flash(flash_config.get('home', 'upload_file_too_big'))
                image.close()
                return redirect(url_for('home.home'))
            elif image.content_type.startswith('image/'):
                filename = session['logged_in'] + ':' + str(ori_last_mid+1) + ':' + secure_filename(image.filename)
                s3.s3_put(filename, image)
                message['image'] = filename
                image.close()
            else:
                current_app.logger.warn(str(session['logged_in'])+' upload file-content error')
                flash(flash_config.get('home', 'upload_file_type_error'))
                image.close()
                return redirect(url_for('home.home'))
        try:
            database.add_msg(str(ori_last_mid+1), session['logged_in'], message)
        except:
            current_app.logger.error('add message fail')
    elif request.method == 'POST' and not postform.validate():
        form.flash_errors(postform)
    return redirect(url_for('home.home'))

@home_blueprint.route("/delmsg/<mid>", methods=['GET'])
@login_required
def delmsg(mid):
    if request.method == 'GET':
        try:
            message = database.get_msg_by_id(mid)
            if message['user'] == session['logged_in']:
                if 'image' in message:
                    s3.s3_delete(message['image'])
                database.del_msg(mid, session['logged_in'])
            else:
                current_app.logger.warn(str(session['logged_in'])+' try to delete illegal message')
            flash (flash_config.get('home', 'delmsg_success'))
            return redirect(url_for('home.home'))
        except TypeError as ex:
            abort(403)
