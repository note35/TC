from lib import google_openid
import web
import unittest
import ConfigParser 
from mock import Mock, patch
import random

#TEST_NEW_GOOGLE_USER_RANDOM_NUMBER
TURN = random.randint(10000,99999)

flash_config = ConfigParser.ConfigParser()
flash_config.read('config/flash.cfg')
key_config = ConfigParser.ConfigParser()
key_config.read('config/key.cfg')

class LoginTestCase(unittest.TestCase):

    def setUp(self):
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

    def test011_login_not_required(self):
        rv = self.login(key_config.get('test_only', 'tester_user'),
                        key_config.get('test_only', 'tester_pwd'))
        rv = self.app.get('/register', follow_redirects = True)
        assert flash_config.get('decorator', 'login_not_required')[1:-1] in rv.data

    def test021_google_login_redirect(self):
        rv = self.app.get('/google_login')
        assert 'You should be redirected automatically to target URL' in rv.data

    def test022_google_login_failed(self):
        rv = self.app.get('/oauth2cb', follow_redirects = True)        
        assert flash_config.get('login', 'login_fail')[1:-1] in rv.data

    def test023_oauth2callback_with_user(self):
        #This code may not support Multithread
        #google_openid.flow_step_2 = Mock(return_value=(
        #    key_config.get('google_openid', 'id')[1:-1],
        #    key_config.get('google_openid', 'name')[1:-1],
        #    key_config.get('google_openid', 'pic')[1:-1])
        #)
        with patch('lib.google_openid.flow_step_2') as m:
            m.return_value = (key_config.get('google_openid', 'id')[1:-1],
                              key_config.get('google_openid', 'name')[1:-1],
                              key_config.get('google_openid', 'pic')[1:-1]
        )
            rv = self.app.get('/oauth2cb?code=123456', follow_redirects=True)
            assert flash_config.get('login', 'login_success')[1:-1] in rv.data

    def test024_oauth2callback_with_newuser(self):
        with patch('lib.google_openid.flow_step_2') as m:
            m.return_value = (str(TURN), 
                              key_config.get('google_openid', 'name')[1:-1],
                              key_config.get('google_openid', 'pic')[1:-1]
        )
            rv = self.app.get('/oauth2cb?code=123456', follow_redirects=True)
        assert flash_config.get('login', 'login_success')[1:-1] in rv.data

    def test024_oauth2callback_without_mock(self):
        rv = self.app.get('/oauth2cb?code=123456', follow_redirects=True)
        assert flash_config.get('login', 'openid_error')[1:-1] in rv.data

