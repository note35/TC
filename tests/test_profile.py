import web
import unittest
import ConfigParser 

key_config = ConfigParser.ConfigParser()
key_config.read('config/key.cfg')
flash_config = ConfigParser.ConfigParser()
flash_config.read('config/flash.cfg')


class ProfileTestCase(unittest.TestCase):

    def setUp(self):
        self.app = web.application.test_client()
        web.application.config['SECRET_KEY'] = 'for_test_only_YEEEEEE'

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

    def test001_profile_without_login(self):
        rv = self.app.get('profile', follow_redirects = True)
        assert flash_config.get('decorator', 'login_required')[1:-1] in rv.data

    def test002_profile_with_login(self):
        self.login( key_config.get('test_only', 'tester_user'),
                    key_config.get('test_only', 'tester_pwd'))
        rv = self.app.get('/profile', follow_redirects = True)
        assert '<td>'+key_config.get('test_only', 'tester_user')+'</td>' in rv.data
