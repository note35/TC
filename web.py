from flask import Flask, session

from decorator import login_required, login_not_required

from views.index import index_blueprint
from views.register import register_blueprint
from views.login import login_blueprint
from views.profile import profile_blueprint
from views.home import home_blueprint

import ConfigParser
key_config = ConfigParser.ConfigParser()
common_config = ConfigParser.ConfigParser()
key_config.read('config/key.cfg')
common_config.read('config/common.cfg')

application = Flask(__name__)
application.register_blueprint(index_blueprint)
application.register_blueprint(register_blueprint)
application.register_blueprint(login_blueprint)
application.register_blueprint(home_blueprint)
application.register_blueprint(profile_blueprint)

application.secret_key = key_config.get('session', 'secret_key')
application.config['SESSION_TYPE'] = common_config.get('session', 'config_type')

if __name__ == "__main__":
    application.debug = common_config.get('flask', 'debug')
    application.run(host = common_config.get('flask','server'), 
                    port = common_config.getint('flask','port'))
    session['logged_in'] = None
