from wtforms import Form, SubmitField, BooleanField, TextAreaField, SelectMultipleField, validators

class PostForm(Form):
    message = TextAreaField('message', [validators.Length(min=1)])
    submit = SubmitField('submit')
