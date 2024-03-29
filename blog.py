# blog.py - controller

from flask import Flask, render_template, request, session, \
    flash, redirect, url_for, g
import sqlite3
from functools import wraps

DATABASE = 'blog.db'

USERNAME = 'admin'
PASSWORD = 'admin'

SECRET_KEY = 'bz\x9eN\xe3OR\xd4\\xf5a\xfb4\x8e/\xd0\x9d\x91\x02i\xca\xbb\x0e6'

app = Flask(__name__)

app.config.from_object(__name__)

def connect_db():
    """Function for connecting to the database"""
    return sqlite3.connect(app.config['DATABASE'])

def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to log in first.')
            return redirect(url_for('login'))
    return wrap

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    status_code = 200

    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME'] or \
            request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid Credentials. Please try again.'
            status_code = 401
        else:
            session['logged_in'] = True
            return redirect(url_for('main'))
    
    return render_template('login.html', error=error), status_code

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))

@app.route('/main')
@login_required
def main():
    with connect_db() as g.db:
        cur = g.db.execute('SELECT * FROM posts')
        posts = [dict(title=row[0], post=row[1]) for row in cur.fetchall()]

    return render_template('main.html', posts=posts)

@app.route('/add', methods=['POST'])
@login_required
def add():
    title = request.form['title']
    post = request.form['post']

    if not title or not post:
        flash("All fields are required. Please try again.")
        return redirect(url_for('main'))
    else:
        with connect_db() as g.db:
            g.db.execute('INSERT into posts (title, post) values (?, ?)',\
                [title, post])
            g.db.commit()
            flash('New entry was successfully posted!')
        return redirect(url_for('main'))

if __name__ == '__main__':
    app.run(debug=True)