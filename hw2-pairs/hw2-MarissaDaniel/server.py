"""
    Server
    Marisssa Ojeda
    Daniel Rojas
"""
import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, render_template, request, g, redirect

app = Flask(__name__)
app.config.from_object(__name__)
app.config["DEBUG"] = True  # Only  include this while you are testing your app

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'vanmo.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

@app.route("/")
def home():
    """Home page showing usernames and passwords."""
    db = get_db()
    cur = db.execute('select username, password from logins order by id asc')
    logins = cur.fetchall()
    return render_template("home.html", logins=logins)

@app.route("/signup", methods=["POST", "GET"])
def signup():
    """Signup page where people can add username and password."""
    if request.method == "POST":
        db = get_db()
        db.execute('insert into logins (username, password) values (?, ?)',
                   [request.form['username'], request.form['password']])
        db.commit()
        return redirect("/")
    else:
        return render_template("signup.html")

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    """Initializes db"""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print 'Initialized the database.'

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0")
