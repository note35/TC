import boto3
import base64

s3 = boto3.resource('s3')


def s3_put(filename, content):
    s3.Bucket('hdems-test-01-weisheng').put_object(
        Key=filename, Body=content)


def s3_get(filename):
    img_data = s3.Object('hdems-test-01-weisheng', filename).get()
    return base64.encodestring(img_data['Body'].read())


def s3_delete(filename):
    s3.Object('hdems-test-01-weisheng', filename).delete()
