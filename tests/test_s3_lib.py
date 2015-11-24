from lib import s3
import base64
import config
import unittest
import boto3
import pytest

class S3LibTestCase(unittest.TestCase):

    def setUp(self):
        self.image_path = 'test_upload/test_upload.jpg'
        self.image_file = open(self.image_path, 'rb')
        self.image_name = 'test_upload.jpg'

    def tearDown(self):  
        self.image_file.close()

    def test001_put_get(self):
        s3.s3_put(self.image_name, self.image_file)
        self.image_file.seek(0)
        uploaded_file = s3.s3_get(self.image_name) 
        assert uploaded_file == base64.encodestring(self.image_file.read())

    def test002_delete(self):
        assert s3.s3_get(self.image_name)
        s3.s3_delete(self.image_name)
        assert not s3.s3_get(self.image_name)
