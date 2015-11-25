from flask import render_template, flash

#tutorial from: http://stackoverflow.com/questions/30108000/flask-register-blueprint-error-python
def register_errorhandlers(application):
    def render_error(error):
        error_code = getattr(error, 'code')
        return render_template("{0}.html".format(error_code)), error_code

    for errcode in [500]:
        application.errorhandler(errcode)(render_error)
    for errcode in [404]:
        application.errorhandler(errcode)(render_error) 
    return None
