"""
    Server
    Marisssa Ojeda
    Daniel Rojas
    Frank Cabada
    Duru Kahyaoglu
"""
import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, flash, render_template, request, g, redirect, session
from custom_json_encoder import CustomJSONEncoder, CustomJSONDecoder
from user import User
from account import Account

APP = Flask(__name__)
APP.config.from_object(__name__)
APP.config["DEBUG"] = True  # Only  include this while you are testing your APP

APP.config.update(dict(
    DATABASE=os.path.join(APP.root_path, 'vanmo.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
APP.config.from_envvar('FLASKR_SETTINGS', silent=True)
APP.json_encoder = CustomJSONEncoder # Converts our objects to JSON dicts
APP.json_decoder = CustomJSONDecoder

@APP.route("/", methods=["POST", "GET"])
def home():
    """Home function to render view accounts or login page."""
    """session.clear()"""
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        return redirect("/view_current_account")

@APP.route('/login', methods=['POST'])
def user_login():
    '''Log in user'''
    username = request.form['usr']
    password = request.form['pwd']
    sql_db = get_db()
    cur = sql_db.execute('select * from logins where username = ? and password = ?',
                         [username, password])
    login = cur.fetchone()
    if login is None:
        flash('Wrong username or password!')
    else:
        session.clear()
        session['logged_in'] = True
        session['userObject'] = User(login[0], username)
    return home()

@APP.route("/signup", methods=["POST", "GET"])
def signup():
    """Signup page where people can add username and password."""
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        sql_db = get_db()
        cur = sql_db.execute('select username from logins where username = ?', [username])
        user = cur.fetchone()
        if user is None:
            sql_db.execute('insert into logins (username, password) values (?, ?)',
                           [username, password])
            sql_db.commit()
            return redirect("/")
        else:
            flash('Please choose another username')
            return redirect("/signup")
    else:
        return render_template("signup.html")

@APP.route("/add_bank_account", methods=["POST", "GET"])
def add_bank_account():
    """Page to redirect to when user chooses to create new bank accounts"""
    if not session.get('logged_in'):
        return redirect("/")
    else:
        user = get_user()
        username = user.get_username()
        if request.method == "POST":
            account_name = request.form['account_name']
            account_type = request.form['account_type']
            cents = request.form['cents']
            if len(cents) > 2:
                flash('Please enter 2 digits for decimal places')
                """return redirect("/add_bank_account")"""
            else:
                cents = float(cents)
                balance = (float(request.form['dollars'])) + (cents/100)

                account = Account(account_name, account_type, username)
                account.deposit(balance)
                user.add_account(account)

                sql_db = get_db()
                sql_db.execute('''insert into accounts (username, accountname, type, balance) values
                               (?, ?, ?, ?)''',
                               [username, account_name, account_type, balance])
                sql_db.commit()
                session['userObject'] = user
                return redirect("/")
        else:
            sql_db = get_db()
            cur = sql_db.execute('select * from accounts where username = ?',
                                 [username])
            accounts = cur.fetchall()
            return render_template("add_bank_account.html", accounts=accounts)

@APP.route("/view_current_account", methods=["GET"])
def view_current_account():
    """Page to redirect to when user chooses to create new bank accounts"""
    if not session.get('logged_in'):
        return redirect("/")
    else:
        sql_db = get_db()
        user = get_user()
        username = user.get_username()
        cur = sql_db.execute('select * from accounts where username = ?', [username])
        cur2 = sql_db.execute('select * from logins where username = ?', [username])
        accounts = cur.fetchall()
        logins = cur2.fetchall()
        return render_template("view_current_account.html", accounts=accounts, logins=logins)


@APP.route("/logout")
def logout():
    """Logout user"""
    session['logged_in'] = False
    session.clear()
    return redirect("/")

def connect_db():
    """Connects to the specific database."""
    db_rv = sqlite3.connect(APP.config['DATABASE'])
    db_rv.row_factory = sqlite3.Row
    return db_rv

def init_db():
    """Initializes sql_db"""
    sql_db = get_db()
    with APP.open_resource('schema.sql', mode='r') as db_file:
        sql_db.cursor().executescript(db_file.read())
    sql_db.commit()

@APP.cli.command('initdb')
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

@APP.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
    else:
        print error

def json_to_user(dictionary):
    """Converts a json dictionary to a User class object"""
    user_object = User(dictionary['id'], dictionary['username'])

    accounts_list = dictionary['accounts'] #list of account dictionaries
    for account in accounts_list:
        account_object = Account(account['account_name'], account['type'],
                                 account['username'])
        account_object.deposit(float(account['balance']))
        user_object.add_account(account_object)
    return user_object

def get_user():
    """Retrieves current session User object"""
    return json_to_user(session['userObject'])

if __name__ == "__main__":
    APP.run(host="0.0.0.0", threaded=True)
