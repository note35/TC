import os
import sys
topdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(topdir)

'''
#test without coverage
from test_index import IndexTestCase
from test_register import RegisterTestCase
from test_login import LoginTestCase
from test_profile import ProfileTestCase
from test_home import HomeTestCase
from test_database import DatabaseTestCase 
from test_s3_lib import S3LibTestCase 
'''

import unittest

if __name__ == '__main__':
    unittest.main()
