from wtforms import Form, BooleanField, PasswordField, TextField, validators

class LoginForm(Form):
    username = TextField('Username')
    password = PasswordField('Password')

class RegistrationForm(Form):
    username = TextField('username', [validators.Length(min=3, max=25)])
    password = PasswordField('password', [validators.Length(min=4)])
    confirm_password = PasswordField('confirm_password', [validators.Length(min=4)])
