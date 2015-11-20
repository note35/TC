import web
import unittest
import random
import ConfigParser 

flash_config = ConfigParser.ConfigParser()
flash_config.read('config/flash.cfg')
key_config = ConfigParser.ConfigParser()
key_config.read('config/key.cfg')

#TEST_USER_RANDOM_NUMBER
TURN = random.randint(10000,99999)

class myProxyHack(object):

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        environ['REMOTE_ADDR'] = environ.get('REMOTE_ADDR', '127.0.0.1')
        return self.app(environ, start_response)

class RegisterTestCase(unittest.TestCase):

    def setUp(self):
        web.application.wsgi_app = myProxyHack(web.application.wsgi_app)
        self.app = web.application.test_client()
        web.application.config['SECRET_KEY'] = 'for_test_only_YEEEEE'
        web.application.config['DEBUG'] = True
        web.application.config['TESTING'] = True

    def tearDown(self):
        pass

    def register(self, username, password, confirm_password):
        with web.application.test_client() as c:
            with c.session_transaction() as sess:
                sess['logged_in'] = None
        return self.app.post('/verify_register', data=dict(
            username = username,
            password = password,
            confirm_password = confirm_password,
        ), follow_redirects = True)

    def test001_register_form_not_validator(self):
        rv = self.register('', '', '')
        assert 'Error in the' in rv.data

    def test002_register_confirm_password_not_match(self):
        rv = self.register( 'test_'+str(TURN),
                            key_config.get('test_only', 'captcha_allow'),
                            key_config.get('test_only', 'not_exist_pwd'))
        assert flash_config.get('register', 'password_not_match')[1:-1] in rv.data

    def test003_register_user_exist(self):
        rv = self.register( key_config.get('test_only', 'tester_user'),
                            key_config.get('test_only', 'captcha_allow'),
                            key_config.get('test_only', 'captcha_allow')) 
        assert flash_config.get('register', 'user_exist')[1:-1] in rv.data

    def test004_register_success(self):
        rv = self.register( 'test_'+str(TURN),
                            key_config.get('test_only', 'captcha_allow'),
                            key_config.get('test_only', 'captcha_allow')) 
        assert flash_config.get('register', 'register_success')[1:-1] in rv.data
