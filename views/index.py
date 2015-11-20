from flask import Blueprint, render_template, flash
from lib import s3
from lib.database import db
from lib import pagination
import json
import ConfigParser
flash_config = ConfigParser.ConfigParser()
flash_config.read('config/flash.cfg')

database = db()
database.init_db()

index_blueprint = Blueprint('index', __name__, template_folder='templates', static_folder='static')
msgs_in_each_page = pagination.msgs_in_each_page

@index_blueprint.route("/")
def index():
    total_pages = len(database.get_msg_list())/msgs_in_each_page+1
    return render_template('index.html', total_pages=total_pages)

@index_blueprint.route("/<request_page>")
def page(request_page):
    message_list = pagination.get_page(request_page)

    if 'error' in message_list:
        flash(flash_config.get('index', 'page_not_exist'))
        return render_template('404.html')

    messages = []
    if message_list:
        for mid in message_list:
            message = database.get_msg_by_id(mid)
            if message['user'].split(':')[0] == 'google':
                message['user'] = message['user'].split(':')[2] 
            if 'image' in message:
                message['image_data'] = s3.s3_get(message['image'])
            messages.append(message)
    return json.dumps(messages)
