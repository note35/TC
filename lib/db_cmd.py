from flask import flash
from flask.ext.redis import FlaskRedis

class db_cmd(object):

    def __init__(self, application):
        redis = FlaskRedis(application)

    def get_msg_list(self):
        try:
            return redis.lrange('messages', 0, redis.llen('messages'))
        except:
            flash("Messages list is not accessible!")

    def get_user_list(self):
        try:
            return redis.lrange('users', 0, redis.llen('users'))
        except:
            flash("Users list is not accessible!")

    def get_user_msg_list(self, username):
        try:
            return redis.lrange('message:'+username, 0, redis.llen('message:'+username))
        except:
            flash(username + "'s message list is not accessible!")

    def get_message_by_id(self, mid):
        try:
            return redis.hget('message', mid) 
        except:
            flash('This message is not exist!')

    def get_user_by_username(self, username):
        try:
            return redis.hget('user', username) 
        except:
            flash('This user is not exist!')

    def add_msg_list(self, mid):
        try:
            redis.lpush('messages', mid)
        except:
            flash('Your message is not able to add to the message list!')

    def add_user_post_list(self, username, mid):
        try:
            redis.lpush('message:'+username, mid)
        except:
            flash('Your message is not able to add to your post list!')

    def add_user_list(self, uid):
        try:
            redis.lpush('users', uid)
        except:
            flash('User created failed!')

    def add_message(self, mid, content):
        try:
            redis.hset('message', mid, content)
        except:
            flash('Your message is not able to store into database!')
 
    def add_user(self, username, profile):
        try:
            redis.hset('user', username, profile)
        except:
            flash(username+' was not created!')
