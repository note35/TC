from flask import Blueprint, render_template, session

from decorator import login_required

from lib.database import db

import ast

database = db()
database.init_db()
redis = database.get_db()

profile_blueprint = Blueprint('profile', __name__, template_folder='templates', static_folder='static')

@profile_blueprint.route('/profile')
@login_required
def profile():
    profile_info = ast.literal_eval(redis.hget('user', session['logged_in']))
    profile_info.pop('password', None)
    return render_template('profile.html', profile_info=profile_info)
