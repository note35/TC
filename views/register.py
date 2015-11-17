from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from models.users import RegistrationForm

from decorator import login_not_required

from lib.database import db

import hashlib
import time

database = db()
database.init_db()

register_blueprint = Blueprint('register', __name__, template_folder='templates', static_folder='static')

@register_blueprint.route("/register")
@login_not_required
def register():
    form = RegistrationForm()
    return render_template('register.html', form=form)

@register_blueprint.route("/verify_register", methods=['POST'])
@login_not_required
def verify_register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate() and ':' not in form.username.data:
        try:
            if database.get_user_by_username(form.username.data) == None:
                if form.password.data == form.confirm_password.data:
                    ori_last_uid = database.get_latest_uid()
                    user_info = { 'uid':ori_last_uid+1,
                                  'username':form.username.data,
                                  'password':hashlib.sha224(form.password.data).hexdigest(),
                                  'regtime':time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}
                    database.add_user(str(ori_last_uid+1), form.username.data, user_info)
                    flash('register successfully!')
                    session['logged_in'] = form.username.data
                    return redirect(url_for('home.home'))
                else:
                    flash('password is not equal to confirm password, try again!')
                    return redirect(url_for('register.register'))
            else:
                flash('username is be used!')
                return redirect(url_for('register.register'))
        except Exception, e:
            print str(e.args)
    else:
        flash('invalid format!')
        return redirect(url_for('register.register'))
    return redirect(url_for('index.index'))

