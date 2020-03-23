import pandas as pd
from hashlib import sha256
from random import shuffle
from quiz.db_management import db_questions


def sha_encode(hash_string):
    # Encodes a string with SHA256 encoding
    sha = sha256(hash_string.encode()).hexdigest()[:15]
    return sha


def make_quiz(theme, config):
    # Reads the file that contains the questions
    q_path = './static/questions.xlsx'
    q = pd.read_excel(q_path)

    # Stores the questions into a db
    db_path = './results.db'
    db_questions(db_path, q)

    # Determines the time to be allocated for each category based on the theme
    time = float(config[config['Theme'] == theme]['Time (min)'])
    cat = {str(cati): time * float(config[config['Theme'] == theme][cati]) for cati in config.columns[2:]}

    # Shuffles the questions, the answers and adds them based on category & time
    time_col = q.columns.get_loc('Time (min)')
    q = q.sample(frac=1)
    q_final = []
    for iCat in cat:
        q_cat = q.loc[q.Category == str(iCat)]
        q_final = randomizer(q, q_final, q_cat, time_col, cat[iCat])

    # If far away from the target time, then tries to fetch questions from other categories
    t_real = sum([x[time_col] for x in q_final if x[time_col] != 'Time (min)'])
    if t_real/time <= 0.95:
        t_missing = time - t_real
        for iCat in cat:
            cat[iCat] = cat[iCat]/time*t_missing
        # Tries to add more questions
        for iCat in cat:
            q_cat = q.loc[q.Category == str(iCat)]
            q_final = randomizer(q, q_final, q_cat, time_col, cat[iCat])

    questions = {str(line[q.columns.get_loc('ID')]): line[q.columns.get_loc('Question'):] for line in q_final}
    return questions


def randomizer(q, q_final, q_cat, time_col, time):
    t = count = 0
    while t < time and count < len(q_cat):
        # Shuffles cols
        s_cols = list(q.columns)[q.columns.get_loc('Choice 1'):]
        shuffle(s_cols)
        s_cols = list(q.columns)[:q.columns.get_loc('Choice 1')] + s_cols
        # Selects questions
        curr_quest = pd.DataFrame(q_cat.iloc[[count]], columns=s_cols).values.tolist()[0]
        count += 1
        if ((t + curr_quest[time_col]) <= time or (t + curr_quest[time_col])/time <= 1.05) \
                and not any(curr_quest[q.columns.get_loc('Question')] in qi for qi in q_final):
            t += curr_quest[time_col]
            q_final.append(curr_quest)
    return q_final
