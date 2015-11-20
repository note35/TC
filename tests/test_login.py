import os
import sys
topdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(topdir)

import web

import unittest
import tempfile
import ConfigParser 

flash_config = ConfigParser.ConfigParser()
flash_config.read('config/flash.cfg')
key_config = ConfigParser.ConfigParser()
key_config.read('config/key.cfg')

class myProxyHack(object):

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        environ['REMOTE_ADDR'] = environ.get('REMOTE_ADDR', '127.0.0.1')
        return self.app(environ, start_response)

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        web.application.wsgi_app = myProxyHack(web.application.wsgi_app)
        self.app = web.application.test_client()
        web.application.config['SECRET_KEY'] = 'for_test_only_YEEEEE'
        web.application.config['DEBUG'] = True
        web.application.config['TESTING'] = True

    def tearDown(self):
        pass

    def login(self, username, password):
        with web.application.test_client() as c:
            with c.session_transaction() as sess:
                sess['logged_in'] = None 
        return self.app.post('/verify_login', data=dict(
            username = username,
            password = password
        ), follow_redirects = True)

    def logout(self):
        return self.app.get('/logout', follow_redirects = True)

    def test001_login_success(self):
        rv = self.login(key_config.get('test_only', 'tester_user'),
                        key_config.get('test_only', 'tester_pwd'))
        assert flash_config.get('login', 'login_success')[1:-1] in rv.data

    def test002_logout_success(self):
        self.login(key_config.get('test_only', 'tester_user'),
                   key_config.get('test_only', 'tester_pwd'))
        rv = self.logout()
        assert flash_config.get('login', 'logout_success')[1:-1] in rv.data
       
    def test003_login_no_such_user(self):
        rv = self.login(key_config.get('test_only', 'not_exist_user'),
                        key_config.get('test_only', 'tester_pwd'))
        assert flash_config.get('login', 'no_such_user')[1:-1] in rv.data

    def test004_wrong_password(self):
        rv = self.login(key_config.get('test_only', 'tester_user'),
                        key_config.get('test_only', 'not_exist_pwd'))
        assert flash_config.get('login', 'wrong_password')[1:-1] in rv.data

if __name__ == '__main__':
    unittest.main()
