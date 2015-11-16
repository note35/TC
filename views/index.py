from flask import Blueprint, render_template
from flask.ext.redis import FlaskRedis
import os
import sys
topdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(topdir)

index_blueprint = Blueprint('index', __name__, template_folder='templates', static_folder='static')

@index_blueprint.route("/")
def index():
    msg_list = redis.lrange('messages', 0, redis.llen('messages'))
    msgs = []
    if msg_list:
        for mid in msg_list:
            msg = ast.literal_eval(redis.hget('message', mid))
            if msg['user'].split(':')[0] == 'google':
                msg['user'] = msg['user'].split(':')[2] 
            if 'image' in msg:
                msg['image_data'] = s3.s3_get(msg['image'])
            msgs.append(msg)
    return render_template('index.html', msgs=msgs)


