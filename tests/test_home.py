import web
import unittest
import ConfigParser 
import json
import pytest
from StringIO import StringIO

flash_config = ConfigParser.ConfigParser()
flash_config.read('config/flash.cfg')
key_config = ConfigParser.ConfigParser()
key_config.read('config/key.cfg')

html_escape_table = {
     "&": "&amp;",
     '"': "&quot;",
     "'": "&apos;",
     ">": "&gt;",
     "<": "&lt;",
     }

def html_escape(text):
     return "".join(html_escape_table.get(c,c) for c in text)



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

    def pomsg(self, msg, upload):
        rv = self.app.post('/pomsg', data=dict(
            message = msg,
            upload = upload
        ), follow_redirects = True)
        return rv

    def delmsg(self):
        page = self.app.get('/home/1', follow_redirects=True)
        msgs = []
        all_id = json.loads(page.data)
        for item in all_id:
            msgs.append(item['mid'])
        target_id = msgs[0]
        return self.app.get('/delmsg/'+target_id, follow_redirects = True)

    def check_upload(self, filename):
        page = self.app.get('/home/1', follow_redirects=True) 
        msgs = []
        if flash_config.get('home', 'page_not_exist')[1:-1] in page.data:
            return False
        else:
            all_image = json.loads(page.data)
            for item in all_image:
                if 'image' in item:
                    if key_config.get('test_only', 'tester_user') in item['image']:
                        if filename in item['image']:
                            self.delmsg()
                            return True
        return False

    def test001_exist_page(self):
        self.login(key_config.get('test_only', 'tester_user'),
                   key_config.get('test_only', 'tester_pwd'))
        self.pomsg(key_config.get('test_only', 'test_message'), (StringIO(''),''))
        rv = self.app.get('/home/1', follow_redirects=True)
        self.delmsg()
        assert flash_config.get('home', 'page_not_exist')[1:-1] not in rv.data   

    def test002_not_exist_page(self):
        self.login(key_config.get('test_only', 'tester_user'),
                   key_config.get('test_only', 'tester_pwd'))
        rv = self.app.get('/home/99999', follow_redirects=True)
        assert flash_config.get('home', 'page_not_exist')[1:-1] in rv.data   

    def test011_post_message(self):
        self.login(key_config.get('test_only', 'tester_user'),
                   key_config.get('test_only', 'tester_pwd'))
        self.pomsg(key_config.get('test_only', 'test_message'), (StringIO(''),''))
        rv = self.app.get('/home/1', follow_redirects=True)
        self.delmsg()
        assert html_escape(key_config.get('test_only', 'test_message')) in rv.data

    def test012_post_message_fail(self):
        self.login(key_config.get('test_only', 'tester_user'),
                   key_config.get('test_only', 'tester_pwd'))
        rv = self.pomsg('', None)
        assert 'Error in the ' in rv.data

    def test013_XSS_message(self):
        self.login(key_config.get('test_only', 'tester_user'),
                   key_config.get('test_only', 'tester_pwd'))
        self.pomsg(key_config.get('test_only', 'xss_message'), (StringIO(''),''))
        rv = self.app.get('/home/1', follow_redirects=True)
        self.delmsg()
        assert html_escape(key_config.get('test_only', 'xss_message')) in rv.data

    def test021_delete_message_success(self):
        #Warning: it only test delete the latest message, it can be improved
        self.login(key_config.get('test_only', 'tester_user'),
                   key_config.get('test_only', 'tester_pwd'))
        self.pomsg(key_config.get('test_only', 'test_delete_message'), (StringIO(''),''))
        rv = self.delmsg()
        assert flash_config.get('home', 'delmsg_success')[1:-1] in rv.data

    def test013_post_message_with_pic(self):
        self.login(key_config.get('test_only', 'tester_user'),
                   key_config.get('test_only', 'tester_pwd'))
        with open('test_upload/test_upload.jpg', 'r') as upload_file:
            self.pomsg(key_config.get('test_only', 'test_message'),
                       (StringIO(upload_file.read()), 'test_upload.jpg'))
        assert self.check_upload('test_upload.jpg')
    
    def test014_post_message_with_wrong_pic(self):
        self.login(key_config.get('test_only', 'tester_user'),
                   key_config.get('test_only', 'tester_pwd'))
        with open('test_upload/test_upload.txt', 'r') as upload_file:
            self.pomsg(key_config.get('test_only', 'test_message'),
                       (StringIO(upload_file.read()), 'test_upload.txt'))
        assert not self.check_upload('test_upload.txt')
