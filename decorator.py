from flask import session, flash, redirect, url_for
from functools import wraps
import ConfigParser
flash_config = ConfigParser.ConfigParser()
flash_config.read('config/flash.cfg')

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash(flash_config.get('decorator', 'login_required'))
            return redirect(url_for('login.login'))
    return wrap

def login_not_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' not in session:
            return f(*args, **kwargs)
        else:
            flash(flash_config.get('decorator', 'login_not_required'))
            return redirect(url_for('home.home'))
    return wrap
