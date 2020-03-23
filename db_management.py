from sqlite3 import Error, connect
from datetime import datetime
from json import dumps


def db_user(db_path, user, theme, pwd, start):
    # Creates a database connection
    conn = create_connection(db_path)
    with conn:
        # Creates the table 'users' if it doesn't exist
        db_create(conn)

        # Inserts/Updates the user's info into the table 'users'
        columns = (user + '_' + theme, theme, user, pwd, start)
        insert_one_row(conn, 'users', columns)


def db_questions(db_path, questions):
    # Creates a database connection
    conn = create_connection(db_path)
    with conn:
        # Creates the table 'questions' if it doesn't exist
        db_create(conn)

        # Inserts/Updates all the questions into the table 'questions'
        questions = questions[['ID', 'Time (min)', 'Category', 'Question', 'Choice 1']]
        columns = list(questions.itertuples(index=False, name=None))
        insert_many_rows(conn, 'questions', columns)


def db_replies(db_path, user, theme, form, time_end):
    # Creates a database connection
    conn = create_connection(db_path)
    with conn:
        # Creates the table 'replies' if it doesn't exist
        db_create(conn)

        # Inserts/Updates the replies into the table 'replies'
        js = dumps(form)
        for k, v in form.items():
            if k == 'username':
                user = v
            elif k == 'time_start':
                time_start = v
            elif k == 'time_end':
                quiz_duration = v
            elif k == 'theme':
                theme = v
            else:
                question_id = k
                id = user + '_' + theme + '_' + question_id
                constrain = "id=?"
                prms = (question_id,)
                question_time = fetch_value(conn, 'question_time', 'questions', constrain, prms)
                constrain = "id=?"
                prms = (id,)
                reply_stored = fetch_value(conn, 'reply', 'replies', constrain, prms)
                if v != reply_stored:
                    fmt = '%Y-%m-%d %H:%M:%S'
                    time_reply = (datetime.strptime(time_end, fmt) - datetime.strptime(time_start, fmt)).seconds/60
                    reply = v
                    constrain = "id=?"
                    prms = (question_id,)
                    correct_answer = fetch_value(conn, 'correct_answer', 'questions', constrain, prms)
                    if v == 'NA':
                        reply_correct = 0
                    elif v == correct_answer:
                        reply_correct = 1
                    else:
                        reply_correct = 0
                    # Updates the whole line
                    columns = (id, user, theme, quiz_duration,
                               question_id, question_time,
                               time_reply, reply, reply_correct, js)
                    insert_one_row(conn, 'replies', columns)


def db_create(conn):
    # Contains information about the users
    sql_create_users_table = """ CREATE TABLE IF NOT EXISTS users (
                                 id text PRIMARY KEY,
                                 theme text NOT NULL,
                                 email text NOT NULL,
                                 password text NOT NULL,
                                 start text NOT NULL
                                 ); """

    # Contains information about each question
    sql_create_questions_table = """CREATE TABLE IF NOT EXISTS questions (
                                    id text PRIMARY KEY,
                                    question_time integer,
                                    category text,
                                    question_text text,
                                    correct_answer text
                                ); """

    # Contains information about each quiz
    sql_create_replies_table = """ CREATE TABLE IF NOT EXISTS replies (
                                   id text PRIMARY KEY,
                                   user_id text NOT NULL,
                                   theme text NOT NULL,
                                   quiz_duration real NOT NULL,
                                   question_id text NOT NULL,
                                   question_time integer,
                                   time_reply real,
                                   reply text,
                                   reply_correct_bol integer,
                                   json text,
                                   FOREIGN KEY (question_id) REFERENCES questions (id)
                                ); """

    # Creates the tables
    if conn is not None:
        create_table(conn, sql_create_users_table)
        create_table(conn, sql_create_questions_table)
        create_table(conn, sql_create_replies_table)
    else:
        print("Error! cannot create the database connection.")


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
        :param db_file: database file
        :return: Connection object or None
    """
    try:
        conn = connect(db_file)
        return conn
    except Error as e:
        print(e)

    return None


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
        :param conn: Connection object
        :param create_table_sql: a CREATE TABLE statement
        :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def insert_one_row(conn, table_name, columns):

    values = '(' + ','.join('?'*len(columns)) + ')'
    sql = ' INSERT OR REPLACE INTO ' + table_name + ' VALUES' + values
    c = conn.cursor()
    c.execute(sql, columns)


def insert_many_rows(conn, table_name, columns):

    values = '(' + ','.join('?'*len(columns[0])) + ')'
    sql = ' INSERT OR REPLACE INTO ' + table_name + ' VALUES' + values
    c = conn.cursor()
    c.executemany(sql, columns)


def update_columns(conn, table_name, constrain, columns_to_update, columns):

    c = conn.cursor()
    sets = '=%s, '.join(columns_to_update) + '=%s'
    c.execute('UPDATE ' + table_name + ' SET ' + sets +
              'WHERE %s=?' % columns, (constrain,))
    conn.commit()


def fetch_value(conn, what, table_name, constrain, prms=None):
    # Check if exists in the db
    try:
        c = conn.cursor()
        sql = "SELECT " + what + " FROM " + table_name + " WHERE " + constrain
        c.execute(sql, prms)
        data = c.fetchone()
        if data is not None:
            data = data[0]
        return data
    except Error as e:
        print(e)


def result(conn, what, table_name, constrain):
    # Generic query
    try:
        c = conn.cursor()
        sql = "SELECT " + what + " FROM " + table_name + " WHERE " + constrain
        data = c.execute(sql)
        return data.fetchone()[0]
    except Error as e:
        print(e)


def db_delete(db_path, table_name, constrain):
    # Deletes elements from the db
    conn = create_connection(db_path)
    with conn:
        try:
            c = conn.cursor()
            sql = "DELETE FROM " + table_name + " WHERE " + constrain
            c.execute(sql)
        except Error as e:
            print(e)
