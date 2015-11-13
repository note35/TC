from wtforms import Form, SubmitField, BooleanField, TextAreaField, SelectMultipleField, validators
from flask.ext.uploads import UploadSet, IMAGES
from flask_wtf.file import FileField, FileAllowed, FileRequired

images = UploadSet('images', IMAGES)
 
class PostForm(Form):
    message = TextAreaField('message', [validators.Length(min=1, max=250)])
    upload = FileField('image', validators=[
        FileAllowed(images, 'Images only!')
    ])
    submit = SubmitField('submit')
