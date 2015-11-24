import boto3
import base64
import ConfigParser
key_config = ConfigParser.ConfigParser()
key_config.read('config/key.cfg')

s3 = boto3.resource('s3')

def s3_put(filename, content):
    s3.Bucket(key_config.get('s3', 'bucket')).put_object(Key=filename, Body=content)

def s3_get(filename):
    try:
        img_data = s3.Object(key_config.get('s3', 'bucket'), filename).get()
        return base64.encodestring(img_data['Body'].read())
    except:
        return False

def s3_delete(filename):
    s3.Object(key_config.get('s3', 'bucket'), filename).delete()
