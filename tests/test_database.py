import unittest
import random
import hashlib
import time

import ConfigParser
key_config = ConfigParser.ConfigParser()
key_config.read('config/key.cfg')

from lib.database import db

database = db()
database.init_db()

#TEST_USER_RANDOM_NUMBER
TURN = random.randint(10000,99999)

class DatabaseTestCase(unittest.TestCase):

    def setUp(self):
        self.user_uid = None
        self.user_name = None
        self.user_info = None
        self.msg_mid = None
        self.msg_message = None

    def tearDown(self):
        pass

    def gen_user(self):
        uid = str(database.get_latest_uid() + 1)
        username = 'db_'+str(TURN)
        user_info = {   'uid': uid,
                        'username': username,
                        'password': hashlib.sha224(key_config.get('test_only', 'tester_pwd')).hexdigest(),
                        'regtime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))} 
        self.user_uid = uid
        self.user_name = username
        self.user_info = user_info

    def gen_msg(self):
        mid = str(database.get_latest_mid() + 1)
        msg = { 'mid': mid,
                'time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
                'user': self.user_name,
                'message': key_config.get('test_only', 'test_db_message')} 
        self.msg_mid = mid
        self.msg_message = msg

    def is_mid_in_list(self, mid, username=None):
        if username:
            mq = database.get_user_msg_list(username)
        else:
            mq = database.get_msg_list()
        if mid in mq:
            return True
        else:
            return False

    def is_uid_in_list(self, uid):
        uq = database.get_user_list()
        if uid in uq:
            return True
        else:
            return False

    def is_user_in_hash(self, username):
        rv = database.get_user_by_username(username)
        if rv:
            return True
        else:
            return False

    def is_msg_in_hash(self, mid):
        rv = database.get_msg_by_id(mid)
        if rv:
            return True
        else:
            return False

    def test001_add_user(self):
        self.gen_user()
        database.add_user(self.user_uid, self.user_name, self.user_info)
        assert self.is_user_in_hash(self.user_name)
        assert self.is_uid_in_list(self.user_uid)

    def test002_add_msg(self):
        user = database.get_user_by_username(key_config.get('test_only', 'tester_user'))
        self.user_uid = user['uid']
        self.user_name = user['username']
        self.gen_msg()
        database.add_msg(self.msg_mid, self.user_name, self.msg_message)
        assert self.is_mid_in_list(self.msg_mid)
        assert self.is_msg_in_hash(self.msg_mid)
        assert self.is_mid_in_list(self.msg_mid, self.user_name)

    def test031_del_msg(self):
        user = database.get_user_by_username(key_config.get('test_only', 'tester_user'))
        self.user_uid = user['uid']
        self.user_name = user['username']
        self.gen_msg()
        database.add_msg(self.msg_mid, self.user_name, self.msg_message) 
        database.del_msg(self.msg_mid, self.user_name) 
        assert not self.is_mid_in_list(self.msg_mid)
        assert not self.is_mid_in_list(self.msg_mid, self.user_name)
