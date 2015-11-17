from wtforms import Form, SubmitField, BooleanField, PasswordField, TextField, validators
from wtfrecaptcha.fields import RecaptchaField
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('key.cfg')

class LoginForm(Form):
    username = TextField ('Username', [validators.Required()])
    password = PasswordField ('Password', [validators.Required()])
    submit = SubmitField ('submit') 

class RegistrationForm(Form):
    username = TextField ('username', [validators.Length(max=25), validators.Required()])
    password = PasswordField ('password', [validators.Length(min=4, max=25), validators.Required()])
    confirm_password = PasswordField ('confirm_password', [validators.Required()])
    submit = SubmitField ('submit') 
    site_key = config.get("recaptcha", "public_key")
    secret_key = config.get("recaptcha", "private_key")
    captcha = RecaptchaField('recaptcha', public_key=site_key, private_key=secret_key, secure=True)
