from flask import Blueprint, Flask, render_template, request, redirect, url_for, session, flash

from decorator import login_required, login_not_required

from views.index import index_blueprint
from views.register import register_blueprint
from views.login import login_blueprint
from views.profile import profile_blueprint
from views.home import home_blueprint

from lib import s3
from lib.database import db

application = Flask(__name__)
application.register_blueprint(index_blueprint)
application.register_blueprint(register_blueprint)
application.register_blueprint(login_blueprint)
application.register_blueprint(home_blueprint)
application.register_blueprint(profile_blueprint)

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
    session['logged_in'] = None
    #application.run(host='52.192.157.72', port=443)
