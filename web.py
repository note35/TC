from flask import Flask, render_template, request, redirect, url_for, session, flash

application = Flask(__name__)

@application.route("/")
def index():
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        return redirect(url_for('home'))

@application.route("/login", methods=['POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == '12345':
            flash('login successfully!')
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            flash('wrong!')
    return redirect(url_for('home')) 

@application.route("/home")
def home():
    return render_template('home.html')

@application.route("/pomsg")
def pomsg():
    return redirect(url_for('home'))

@application.route("/delmsg/<msgid>", methods=['GET'])
def delmsg():
    return redirect(url_for('home'))

@application.route("/profile")
def profile():
    return render_template('profile.html')

@application.route("/logout")
def logout():
    session.pop('logged_in', None)
    flash('logout successfully')
    return redirect(url_for('index'))

if __name__ == "__main__":
    application.secret_key = 'super secret key'
    application.run()
