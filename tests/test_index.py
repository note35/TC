import os
import sys
topdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(topdir)

import web

import unittest
import ConfigParser 

flash_config = ConfigParser.ConfigParser()
flash_config.read('config/flash.cfg')

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.app = web.application.test_client()
        web.application.config['SECRET_KEY'] = 'for_test_only_YEEEEE'

    def tearDown(self):
        pass

    def test001_index(self):
        rv = self.app.get('/', follow_redirects=True)
        assert 'login' in rv.data

    def test002_exist_page(self):
        rv = self.app.get('/1', follow_redirects=True)
        assert flash_config.get('index', 'page_not_exist')[1:-1] not in rv.data   

    def test003_not_exist_page(self):
        rv = self.app.get('/99999', follow_redirects=True)
        assert flash_config.get('index', 'page_not_exist')[1:-1] in rv.data   

if __name__ == '__main__':
    unittest.main()
