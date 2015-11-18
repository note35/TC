from lib.database import db
database = db()
database.init_db()

msgs_in_each_page = 10

def get_page(request_page = 1, who = None):
    page = int(request_page)

    if not who:
        message_list = database.get_msg_list()
    else:
        message_list = database.get_user_msg_list(who)

    if len(message_list) > msgs_in_each_page*(page-1) and page > 0:
        return message_list[(page-1)*msgs_in_each_page:(page-1)*msgs_in_each_page+msgs_in_each_page]
    else:
        return ['error'] 
