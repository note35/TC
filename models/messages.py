from wtforms import Form, SubmitField, BooleanField, TextAreaField, SelectMultipleField, validators
from flask.ext.uploads import UploadSet, IMAGES
from flask_wtf.file import FileField, FileAllowed

images = UploadSet('images', IMAGES)

class PostForm(Form):
    message = TextAreaField('message', [validators.Length(max=250), validators.Required()])
    upload = FileField('image', validators=[FileAllowed(images, 'Images only!')])
    submit = SubmitField('submit')
