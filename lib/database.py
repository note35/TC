from redis import Redis, Connection

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

    def get_user_msg_list(self, username):
        try:
            return self.redis.lrange('message:'+username, 0, self.redis.llen('message:'+username))
        except:
            print(username + "'s message list is not accessible!")

    def get_message_by_id(self, mid):
        try:
            return self.redis.hget('message', mid) 
        except:
            print('This message is not exist!')

    def get_user_by_username(self, username):
        try:
            return self.redis.hget('user', username) 
        except:
            print('This user is not exist!')

    def add_msg_list(self, mid):
        try:
            self.redis.lpush('messages', mid)
        except:
            print('Your message is not able to add to the message list!')

    def add_user_post_list(self, username, mid):
        try:
            self.redis.lpush('message:'+username, mid)
        except:
            print('Your message is not able to add to your post list!')

    def add_user_list(self, uid):
        try:
            self.redis.lpush('users', uid)
        except:
            print('User created failed!')

    def add_message(self, mid, content):
        try:
            self.redis.hset('message', mid, content)
        except:
            print('Your message is not able to store into database!')

    def add_user(self, username, profile):
        try:
            self.redis.hset('user', username, profile)
        except:
            print(username+' was not created!')
