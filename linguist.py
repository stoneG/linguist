import os
import pdb

from flask import Flask, render_template, request, flash, session, redirect, url_for
from wordnik.api.APIClient import APIClient
from wordnik.api.WordAPI import WordAPI
import wordnik.model

from db import *
from wordnik_api_key import *

client = APIClient(api_key, 'http://api.wordnik.com/v4')
wordAPI = WordAPI(client)
lookup = wordnik.model.WordDefinitionsInput.WordDefinitionsInput()

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
    if 'logged_in' not in session:
        session['logged_in'] = False
    if 'username' in session:
        return render_template('main.html', username=session['username'],
                               username_link='/'+session['username'])
    return render_template('main.html', username=False)

@app.route('/lookup', methods=['POST'])
def score():
    word = request.form['word'].lower()
    count = WC.get_count(word)
    score = 0
    css = "font-size:50px;"
    username = False
    if type(count) == type(1):
        WC.increment_word(word)
        lookup.word = word
        lookup.limit = 1
        defn = wordAPI.getDefinitions(lookup)[0].text
        if session['logged_in']:
            score = WC.score(word, count)
            try:
                Users.add_to_word_score(session['username'], word, score)
            except ReuseError:
                pass
            else:
                css = "font-size:{0}px;".format(20)
                username = session['username']
        grow = "grow({0},{1},{2})".format(0, max(score,20), 100)
        return render_template('score.html', word=word, size=css, score=score,
                               defn=defn, logged_in=session['logged_in'],
                               username=username, grow=grow)
    else:
        return '"{0}" is not in our database.'.format(word)

@app.route('/register.html', methods=['GET', 'POST'])
def register():
    if 'logged_in' in session and session['logged_in']:
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
    if 'logged_in' in session and session['logged_in']:
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
    fname, lname, email, words, scores = Users.get_user_info(session['username'])
    score = 100 # TODO show cumulative score
    words = words.split()
    scores = scores.split()
    length = len(words)
    return render_template('profile.html', user=username, fname=fname, lname=lname,
                           email=email, score=score, words=words, scores=scores,
                           length=length)

@app.route('/404')
def four_oh_four():
    return render_template('404.html')

if __name__ == '__main__':
    print 'Running Linguist on localhost:5000'
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
