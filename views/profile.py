from flask import Blueprint, render_template, session, current_app, abort

from decorator import login_required
from lib.database import db

database = db()
database.init_db()

profile_blueprint = Blueprint('profile', __name__, template_folder='templates', static_folder='static')

@profile_blueprint.route('/profile')
@login_required
def profile():
    try:
        profile_info = database.get_user_by_username(session['logged_in'])
        profile_info.pop('password', None)
    except AttributeError as ex:
        current_app.logger.error('Something wrong while getting user from database') 
        abort(500)
    return render_template('profile.html', profile_info=profile_info)
