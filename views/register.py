from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from models.users import RegistrationForm

from decorator import login_not_required

from lib.database import db
from lib import form

import hashlib
import time
import ConfigParser

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
    registform = RegistrationForm(request.form, captcha={'ip_address': request.remote_addr})
    form_validator = registform.validate()

    config = ConfigParser.ConfigParser()
    config.read('key.cfg')
    if unicode(config.get('test_only', 'captcha_allow')) == registform.captcha.data:
        form_validator = True

    if request.method == 'POST' and form_validator and ':' not in registform.username.data:
        try:
            if database.get_user_by_username(registform.username.data) == None:
                if registform.password.data == registform.confirm_password.data:
                    ori_last_uid = database.get_latest_uid()
                    user_info = { 'uid':ori_last_uid+1,
                                  'username':registform.username.data,
                                  'password':hashlib.sha224(registform.password.data).hexdigest(),
                                  'regtime':time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}
                    database.add_user(str(ori_last_uid+1), registform.username.data, user_info)
                    flash('register successfully!')
                    session['logged_in'] = registform.username.data
                    return redirect(url_for('home.home'))
                else:
                    flash('password is not equal to confirm password, try again!')
                    return redirect(url_for('register.register'))
            else:
                flash('username is be used!')
                return redirect(url_for('register.register'))
        except Exception, e:
            print str(e.args)
    elif request.method == 'POST' and not registform.validate():
        form.flash_errors(registform)
        return redirect(url_for('register.register'))
    return redirect(url_for('index.index'))

