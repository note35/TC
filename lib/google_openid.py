from flask import url_for, flash, redirect
from oauth2client.client import flow_from_clientsecrets
from apiclient import discovery
import httplib2
import ConfigParser
common_config = ConfigParser.ConfigParser()
common_config.read('config/common.cfg')

def create_flow():
    return flow_from_clientsecrets( common_config.get('login', 'google_client_secret'), 
                                    scope='openid profile', 
                                    redirect_uri=url_for('login.oauth2cb', 
                                    _external=True))

def flow_step_1():
    flow = create_flow()
    return flow.step1_get_authorize_url()

def flow_step_2(callback_code):
    flow = create_flow()
    if callback_code:
        try:
            credentials = flow.step2_exchange(callback_code)
            http_auth = credentials.authorize(httplib2.Http())
            profile = discovery.build('oauth2', 'v2', http_auth)
            user_info = profile.userinfo().get().execute()
            return user_info['id'], user_info['given_name'], user_info['picture']
        except:
            return 'fail', 'fail', 'fail'
