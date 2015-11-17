from redis import Redis
import ast

class db(object):

    def __init__(self):
        pass

    def init_db(self):
        self.redis = Redis()

    def get_db(self):
        return self.redis

    def get_msg_list(self):
        try:
            return self.redis.lrange('messages', 0, self.redis.llen('messages'))
        except:
            print("Messages list is not accessible!")

    def get_user_list(self):
        try:
            return self.redis.lrange('users', 0, self.redis.llen('users'))
        except:
            print("Users list is not accessible!")

    def get_latest_mid(self):
        try:
            if self.redis.lrange('messages', 0, 1):
                return int(self.redis.lrange('messages', 0, 1)[0])
            else:
                return int(0)
        except:
            print("Messages list is not accessible!")

    def get_latest_uid(self):
        try:
            if self.redis.lrange('users', 0, 1):
                return int(self.redis.lrange('users', 0, 1)[0])
            else:
                return int(0)
        except:
            print("Messages list is not accessible!")

    def get_user_msg_list(self, username):
        try:
            return self.redis.lrange('messages:'+username, 0, self.redis.llen('messages:'+username))
        except:
            print(username + "'s message list is not accessible!")

    def get_msg_by_id(self, mid):
        try:
            return ast.literal_eval(self.redis.hget('message', mid))
        except:
            print('This message is not exist!')

    def get_user_by_username(self, username):
        try:
            return ast.literal_eval(self.redis.hget('user', username))
        except:
            print('This user is not exist!')

    def del_msg(self, mid, username):
        try:
            self.redis.hdel('message', mid)
            self.redis.lrem('messages', mid)
            self.redis.lrem('messages:'+username, mid)
        except:
            print('remove message fails')

    def add_msg(self, mid, username, message):
        try:
            self.redis.lpush('messages', mid)
            self.redis.lpush('messages:'+username, mid)
            self.redis.hset('message', mid, message) 
        except:
            print('add message fails')

    def add_user(self, uid, username, user_info):
        try:
            self.redis.lpush('users', uid)
            self.redis.hset('user', username, user_info)
        except:
            print('add user fails') 
