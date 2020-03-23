from flask import Flask, render_template, request, send_file
from datetime import datetime
from os import environ
import pandas as pd
from random import randrange
from quiz.db_management import db_user, db_replies, create_connection, fetch_value, db_delete, result
from quiz.functions import sha_encode, make_quiz

app = Flask(__name__, template_folder='templates')


# Welcome page
@app.route('/', methods=['GET'])
def welcome():
    # Gets the basic theme questionnaire configuration
    path = './static/config.csv'
    config = pd.read_csv(path, ',')

    # Displays the log-in form
    return render_template('welcome.html', theme=config['Theme'])


# Displays the questions
@app.route('/quiz', methods=['POST'])
def display_quiz():

    # Fetches the theme config
    path = './static/config.csv'
    config = pd.read_csv(path, ',')
    db_path = './results.db'

    # Checks if the user's name and password were inserted
    user = request.form.get("user", None)
    password = request.form.get("password", None)
    theme = None
    warning = ''

    if user == '' or password == '':
        if user == '' and password == '':
            warning = 'Error: User & Password missing'
        elif user == '':
            warning = 'Error: User missing'
        elif password == '':
            warning = 'Error: Password missing'
        return render_template('welcome.html', theme=config['Theme'], w=warning, c=user, p=password)
    else:
        # Detects to which theme does the password belong
        for t in config['Theme']:
            if sha_encode(user + '_' + t) == password:
                theme = t
                break

        if theme is None:
            if user != 'superuser' and password != 'superpwd':
                # Wrong password
                warning = 'Error: Password and/or User are incorrect'
                return render_template('welcome.html', theme=config['Theme'], w=warning, c=user, p=password)
            else:
                # Overrides the log-in
                db_delete(db_path, 'replies', "id LIKE 'superuser_Generic%';")
                theme = 'Generic'
                questions = make_quiz(theme, config)
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                db_user(db_path, user, theme, password, timestamp)
                # Displays the quiz
                t = config[config['Theme'] == theme]['Time (min)'].values[0]
                return render_template('quiz.html', theme=theme, c=user, q=questions, t0=timestamp, tt=t)
        else:
            # Checks if the user has replied to the quiz
            with create_connection(db_path) as conn:
                constrain = "email=? AND theme=?"
                prms = (user, theme)
                already = fetch_value(conn, 'email', 'users', constrain, prms)
            if already == user:
                # Returns an error
                warning = "The user already replied to the quiz for the theme '" + theme + "'."
                return render_template('welcome.html', theme=config['Theme'], w=warning)
            else:
                # Stores user's info into the db
                # Fetches the questions for the quiz
                questions = make_quiz(theme, config)
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                db_user(db_path, user, theme, password, timestamp)
                # Displays the quiz
                t = config[config['Theme'] == theme]['Time (min)'].values[0]
                return render_template('quiz.html', theme=theme, c=user, q=questions, t0=timestamp, tt=t)


# Saves the replies
@app.route('/done', methods=['POST'])
def save_quiz():

    # Fetches the user's name
    user = request.form.get("username", None)
    if user is None:
        user = request.args.get("username", None)
    if user == '':
        user = "unknown_" + str(randrange(1, 2**30, 1))
    theme = request.form.get("theme", None)

    # Saves the quiz in a db
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db_path = './results.db'
    db_replies(db_path, user, theme, request.form, timestamp)

    # Gets the result
    with create_connection(db_path) as conn:
        nb_right = result(conn, 'SUM(reply_correct_bol)', 'replies',
                          "user_id = '" + user + "' AND theme = '" + theme + "';")
        nb_total = result(conn, 'COUNT(reply_correct_bol)', 'replies',
                          "user_id = '" + user + "' AND theme = '" + theme + "';")

    # Displays the end page
    return render_template('done.html', nb_right=nb_right, nb_total=nb_total)


# Access to the db
@app.route('/db', methods=['GET'])
def db():
    user = request.args.get("user", None)
    password = request.args.get("pwd", None)
    if user == 'superuser' and password == 'superpwd':
        return send_file("./results.db")


# Access to the list of themes
@app.route('/themes', methods=['GET'])
def themes():
    user = request.args.get("user", None)
    password = request.args.get("pwd", None)
    if user == 'superuser' and password == 'superpwd':
        return send_file("./static/config.csv")


# Access to the sha encryption
@app.route('/sha', methods=['GET'])
def sha_get():
    password = request.args.get("pwd", None)
    user = request.args.get("user", None)
    email = request.args.get("email", None)
    theme = request.args.get("theme", None)

    sha = 'Access not allowed'
    if user == 'superuser' and password == 'superpwd':
        db_path = './results.db'
        with create_connection(db_path) as conn:
            constrain = "email=? AND theme=?"
            prms = (email, theme)
            already = fetch_value(conn, 'email', 'users', constrain, prms)
            if already == email:
                sha = 'User already replied to this quiz'
            else:
                # Gets the list of themes
                path = './static/config.csv'
                config = pd.read_csv(path, ',')
                sha = sha_encode(email + '_' + theme) if theme in config.values else 'theme not found'

    return sha


if __name__ == '__main__':
    import webbrowser

    webbrowser.open('http://localhost:5000/', new=0, autoraise=True)
    port = int(environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
