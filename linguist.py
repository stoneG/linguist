from flask import Flask, render_template, request, flash, session, redirect, url_for
import pdb
from wordnik.api.APIClient import APIClient
import wordnik.model

from db import *
from wordnik_api_key import *

wn = APIClient(api_key, 'http://api.wordnik.com/v4')

#DATABASE = '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'sitong'
PASSWORD = 'peng'

app = Flask(__name__)
app.config.from_object(__name__)
WC = WordCountTable('linguist', 'sitong', tableName='WordCount')
Users = UserTable('linguist', 'sitong', tableName='Users')

@app.route('/')
def main():
    if 'username' in session:
        return render_template('main.html', username=session['username'],
                               username_link='/'+session['username'])
    return render_template('main.html', username=False)

@app.route('/lookup', methods=['POST'])
def score():
    word = request.form['word']
    count = WC.get_count(word)
    if count:
        WC.increment_word(word)
        css = "font-size:{0}px;".format(300)
        x = 10
        return render_template('score.html', word=word, size=css, score=x)
    else:
        return '{0} is not in db.'.format(word)

@app.route('/register.html', methods=['GET', 'POST'])
def register():
    if session['logged_in']:
        return render_template('register.html', logged_in=True)
    error = ''
    if request.method == 'POST':
        error = Users.register(request.form['username'], request.form['password'],
                               request.form['fName'], request.form['lName'],
                               request.form['email'])
        if not error:
            session['logged_in'] = True
            session['username'] = request.form['username']
            return redirect(url_for('main'))
    return render_template('register.html', error=error)

@app.route('/login.html', methods=['GET', 'POST'])
def login():
    if session['logged_in']:
        return render_template('login.html', logged_in=True)
    error = ''
    if request.method == 'POST':
        error = Users.login(request.form['username'], request.form['password'])
        if not error:
            session['username'] = request.form['username']
            session['logged_in'] = True
            return redirect(url_for('main'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session['logged_in'] = False
    del session['username']
    return redirect(url_for('main'))

@app.route('/<username>')
def profile(username):
    if 'username' not in session or username != session['username']:
        return render_template('404.html')
    fname, lname, email = Users.get_user_info(session['username'])
    score = 100
    return render_template('profile.html', user=username, fname=fname, lname=lname,
                           email=email, score=score)

@app.route('/404')
def four_oh_four():
    return render_template('404.html')

#if __name__ == '__main__':
#    print 'Running Linguist on localhost:5000'
#    app.run()

app.run()
