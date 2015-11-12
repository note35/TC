import os
import sys
topdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(topdir)
import unittest
import tempfile
import random

from flask.ext.redis import FlaskRedis
import web

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.app = web.application.test_client()
        web.redis = FlaskRedis(web.application)
        web.application.config['SECRET_KEY'] = 'test'
        #web.redis.flushdb()

    def tearDown(self):
        pass

    def register(self, username, password, confirm_password):
        return self.app.post('/verify_register', data=dict(
            username = username,
            password = password,
            confirm_password = confirm_password
        ), follow_redirects = True)

    def login(self, username, password):
        with web.application.test_client() as c:
            with c.session_transaction() as sess:
                sess['logged_in'] = None 
        return self.app.post('/verify_login', data=dict(
            username = username,
            password = password
        ), follow_redirects = True)

    def pomsgs(self, msg):
        self.login('kir', '1111')
        with web.application.test_client() as c:
            with c.session_transaction() as sess:
                sess['logged_in'] = None 
        for idx in range(random.randint(1,3)):
            self.app.post('/pomsg', data=dict(
                message = 'user_' + str(TURN) + ' ' + str(idx) + '_' + msg
            ), follow_redirects = True) 
        return self.app.get('/home', follow_redirects = True)

    def delmsg(self, msg):
        self.login('kir', '1111')
        with web.application.test_client() as c:
            with c.session_transaction() as sess:
                sess['logged_in'] = None 
        page = self.app.post('/pomsg', data=dict(
            message = 'user_' + str(TURN) + '_' + msg
        ), follow_redirects = True) 
        print page.data
        #To do: find the first <div id=22 pattern in this data
        #return self.app.get('/home', follow_redirects = True)

    def test_index(self):
        rv = self.app.get('/', follow_redirects=True)
        assert 'login' in rv.data

    def test_register_confirm_password_not_match(self):
        with web.application.test_client() as c:
            with c.session_transaction() as sess:
                sess['logged_in'] = None
        rv = self.register('test_'+str(TURN), '1111', '11111')
        assert 'password is not equal to confirm password, try again!' in rv.data

    def test_register_user_exist(self):
        with web.application.test_client() as c:
            with c.session_transaction() as sess:
                sess['logged_in'] = None
        rv = self.register('kir', '1111', '1111')
        assert 'username is be used!' in rv.data

    def test_register_success(self):
        with web.application.test_client() as c:
            with c.session_transaction() as sess:
                sess['logged_in'] = None
        rv = self.register('test_'+str(TURN), '1111', '11111')
        assert 'password is not equal to confirm password, try again!' in rv.data

    def test_register_success(self):
        with web.application.test_client() as c:
            with c.session_transaction() as sess:
                sess['logged_in'] = None
        rv = self.register('test_'+str(TURN), '1111', '1111')
        assert 'register successfully!' in rv.data

    def test_logout(self):
        self.login('test_'+str(TURN), '1111')
        rv = self.app.get('/logout', follow_redirects = True)
        assert 'logout successfully!' in rv.data
       
    def test_login_no_such_user(self):
        rv = self.login('test_'+str(TURN), '1111')
        assert 'no such user!' in rv.data

    def test_login_success(self):
        rv = self.login('kir', '1111')
        assert 'login successfully!' in rv.data

    '''
    @@@ Alert: Need to be sloved!!! @@@
    def test_login_success2(self):
        self.register('test_'+str(TURN+1), '1111', '1111')
        self.login('test_'+str(TURN+1), '1111')
        assert 'login successfully!' in rv.data
    '''

    def test_post_messages(self):
        rv = self.pomsgs('test post message :)')
        assert 'test post message :)' in rv.data

    '''
    def test_delete_message_success(self):
        self.delmsg('test delete message')
    '''

    def test_profile(self):
        self.login('kir', '1111')
        rv = self.app.get('/profile', follow_redirects = True)
        assert '<td>kir</td>' in rv.data

if __name__ == '__main__':
    #TEST_USER_RANDOM_NUMBER
    TURN = random.randint(10000,99999)
    print TURN
    unittest.main()
