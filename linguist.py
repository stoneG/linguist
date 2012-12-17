from flask import Flask, render_template, request, flash, session, redirect, url_for
import pdb

from db import *

#DATABASE = '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'sitong'
PASSWORD = 'peng'

app = Flask(__name__)
app.config.from_object(__name__)
WC = WordCountTable('linguist', 'sitong', tblName='WordCount')
Users = UserTable('linguist', 'sitong', tableName='Users')

@app.route('/')
def main():
    if 'username' in session:
        return render_template('main.html', username=session['username'])
    return render_template('main.html', username=False)

@app.route('/add', methods=['POST'])
def rarity():
    word = request.form['word']
    count = WC.get_count(word)
    if count:
        WC.increment_word(word)
        return '{0}:{1}'.format(word, count)
    else:
        return '{0} is not in db.'.format(word)

@app.route('/login.html', methods=['GET', 'POST'])
def login():
    if session['logged_in']:
        return render_template('login.html', logged_in=True)
    error = ''
    registering = False
    if 'register' in request.method:
        registering = True
    if request.method == 'POST' and registering:
        error = Users.register(request.form['username'], request.form['password'])
        if not error:
            session['logged_in'] = True
            return redirect(url_for('main'))
    elif request.method == 'POST':
        error = Users.login(request.form['username'], request.form['password'])
        if not error:
            session['username'] = request.form['username']
            session['logged_in'] = True
            return redirect(url_for('main'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session['logged_in'] = False
    return redirect(url_for('main'))

#if __name__ == '__main__':
#    print 'Running Linguist on localhost:5000'
#    app.run()

app.run()
