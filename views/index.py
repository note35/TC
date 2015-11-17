from flask import Blueprint, render_template
from lib import s3
from lib.database import db

import ast

database = db()
database.init_db()
redis = database.get_db()

index_blueprint = Blueprint('index', __name__, template_folder='templates', static_folder='static')

@index_blueprint.route("/")
def index():
    messages = []
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
