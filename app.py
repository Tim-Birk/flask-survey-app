from flask import Flask, render_template, request, redirect, flash
from flask_debugtoolbar import DebugToolbarExtension
from surveys import satisfaction_survey

app = Flask(__name__)
app.config['SECRET_KEY'] = "oh-so-secret"
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

debug = DebugToolbarExtension(app)

ANSWERS = []

@app.route("/")
def index():
    """Display survey start page with instructions and initialize an empty ANSWERS list"""

    survey = satisfaction_survey
    del ANSWERS[:]
    return render_template("survey.html", survey=survey)

@app.route("/question/<int:number>")
def question(number):
    """Display a question page with question and choices
    
    If the user has completed the survey or tries to answer a question
    out of order, they will be redirected appropriately
    """

    survey = satisfaction_survey
    # protect route
    if len(ANSWERS) == len(survey.questions):
        flash("The survey has already been completed.", "error")
        return redirect("/thankyou") 
    elif not number == len(ANSWERS):
        flash("The questions must be completed in order.", "error")
        return redirect(f"/question/{len(ANSWERS)}")

    question = survey.questions[int(number)]

    """ next_number will show the non-index question number 
    and also give the number of the next question for the link route """
    next_number = number + 1
    return render_template("question.html", survey=survey, question=question, next_number=next_number)

@app.route("/question/<int:number>", methods=["POST"])
def question_post(number):
    """Handle post request from question page's form
    
    If the final question was answered:
      the user will be redirected to a thank you page

    Otherwise:
      'answer' from post request will be added to ANSWERS list
      and user will be redirected to next question in the survey
    """
    survey = satisfaction_survey
    answer = request.form["answer"]
    ANSWERS.append(answer)

    next_number = number + 1
    if next_number >= len(survey.questions):
        return redirect("/thankyou") 
    else:
        return redirect(f"/question/{number + 1}")

@app.route("/thankyou")
def thankyou():
    """Display a thank you page to the user to end the survey"""
    survey = satisfaction_survey
    return render_template("thankyou.html", survey=survey)
