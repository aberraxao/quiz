# quiz

**Description:** Build a weighted random quiz based on a selection of questions and correct it.

**Online Preview:** http://aberraxao.pythonanywhere.com/
  * User: superuser
  * Password: superpassword

**How to modify:**
* The questions are stored in [question.xlsx](/static/questions.xlsx):
  * To simplify, the correct answer calways orresponds to the "Choice 1"
  * Tabs are not supported, instead we 4 spaces should be used
  * ![questions](/static/images/questions.PNG)
  
* The duration of the quiz and weights of each category an be defined in [config.csv](/static/config.csv):
    | Theme     | Time (min) | Logic | VBA  | Python | Code |
    |-----------|------------|-------|------|--------|------|
    | No VBA    | 10         | 0.2   | 0.2  | 0      | 0.6  |
    | No Python | 10         | 0.2   | 0.2  | 0.6    | 0    |
    | Generic   | 10         | 0.25  | 0.25 | 0.25   | 0.25 |
