from redis import Redis
import ast
from flask import current_app

class db(object):

    def __init__(self):
        pass

    def init_db(self):
        self.redis = Redis()

    def get_msg_list(self):
        try:
            return self.redis.lrange('messages', 0, self.redis.llen('messages'))
        except:
            current_app.logger.error("Messages list is not accessible!")

    def get_user_list(self):
        try:
            return self.redis.lrange('users', 0, self.redis.llen('users'))
        except:
            current_app.logger.error("Users list is not accessible!")

    def get_latest_mid(self):
        try:
            if self.redis.lrange('messages', 0, 1):
                return int(self.redis.lrange('messages', 0, 1)[0])
            else:
                return int(0)
        except:
            current_app.logger.error("Messages list is not accessible!")

    def get_latest_uid(self):
        try:
            if self.redis.lrange('users', 0, 1):
                return int(self.redis.lrange('users', 0, 1)[0])
            else:
                return int(0)
        except:
            current_app.logger.error("Messages list is not accessible!")

    def get_user_msg_list(self, username):
        try:
            return self.redis.lrange('messages:'+username, 0, self.redis.llen('messages:'+username))
        except:
            current_app.logger.error(username + "'s message list is not accessible!")

    def get_msg_by_id(self, mid):
        try:
            return ast.literal_eval(self.redis.hget('message', mid))
        except:
            current_app.logger.error('This message is not exist!')

    def get_user_by_username(self, username):
        try:
            return ast.literal_eval(self.redis.hget('user', username))
        except:
            current_app.logger.error('This user is not exist!')

    def get_username_by_uid(self, uid):
        pass

    def del_msg(self, mid, username):
        try:
            self.redis.hdel('message', mid)
            self.redis.lrem('messages', mid)
            self.redis.lrem('messages:'+username, mid)
        except:
            current_app.logger.error('remove message fails')

    def add_msg(self, mid, username, message):
        try:
            self.redis.lpush('messages', mid)
            self.redis.lpush('messages:'+username, mid)
            self.redis.hset('message', mid, message) 
        except:
            current_app.logger.error('add message fails')

    def add_user(self, uid, username, user_info):
        try:
            self.redis.lpush('users', uid)
            self.redis.hset('user', username, user_info)
        except:
            current_app.logger.error('add user fails') 
