import web
import unittest
import ConfigParser 
import json

flash_config = ConfigParser.ConfigParser()
flash_config.read('config/flash.cfg')
key_config = ConfigParser.ConfigParser()
key_config.read('config/key.cfg')

class HomeTestCase(unittest.TestCase):

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

    def pomsg(self, msg):
        rv = self.app.post('/pomsg', data=dict(
            message = msg,
            upload = None
        ), follow_redirects = True)
        return rv

    def delmsg(self, msg):
        '''
        Warning: it only test delete the latest message, it can be improved
        Now:    1) user kira login
                2) post a new message
                3) delete that message 
        '''
        self.pomsg(msg)
        page = self.app.get('/home/1', follow_redirects=True)
        msgs = []
        all_id = json.loads(page.data)
        for item in all_id:
            msgs.append(item['mid'])
        target_id = msgs[-1]
        return self.app.get('/delmsg/'+target_id, follow_redirects = True)

    def test001_exist_page(self):
        self.login(key_config.get('test_only', 'tester_user'),
                   key_config.get('test_only', 'tester_pwd'))
        self.pomsg(key_config.get('test_only', 'test_message'))
        rv = self.app.get('/home/1', follow_redirects=True)
        assert flash_config.get('home', 'page_not_exist')[1:-1] not in rv.data   

    def test002_not_exist_page(self):
        self.login(key_config.get('test_only', 'tester_user'),
                   key_config.get('test_only', 'tester_pwd'))
        rv = self.app.get('/home/99999', follow_redirects=True)
        assert flash_config.get('home', 'page_not_exist')[1:-1] in rv.data   

    def test011_post_message(self):
        self.login(key_config.get('test_only', 'tester_user'),
                   key_config.get('test_only', 'tester_pwd'))
        self.pomsg(key_config.get('test_only', 'test_message'))
        rv = self.app.get('/home/1', follow_redirects=True)
        assert key_config.get('test_only', 'test_message')[1:-1] in rv.data

    def test012_post_message_fail(self):
        self.login(key_config.get('test_only', 'tester_user'),
                   key_config.get('test_only', 'tester_pwd'))
        rv = self.pomsg('')
        assert 'Error in the ' in rv.data

    def test021_delete_message_success(self):
        self.login(key_config.get('test_only', 'tester_user'),
                   key_config.get('test_only', 'tester_pwd'))
        rv = self.delmsg('test delete message :(')
        assert flash_config.get('home', 'delmsg_success')[1:-1] in rv.data
