import os
import sys
topdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(topdir)

from test_index import IndexTestCase
from test_register import RegisterTestCase
from test_login import LoginTestCase
from test_profile import ProfileTestCase
from test_home import HomeTestCase

import unittest

if __name__ == '__main__':
    unittest.main()
