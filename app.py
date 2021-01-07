from flask import Flask, render_template, request, redirect, flash, session, make_response
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys

app = Flask(__name__)
app.config['SECRET_KEY'] = "oh-so-secret"
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

debug = DebugToolbarExtension(app)

@app.route("/")
def index():
    """Display index page where user can select a survey"""
    return render_template("home.html")

@app.route("/surveys/<name>")
def survey_home(name):
    """Display survey start page with instructions"""
    survey = surveys[name]
    return render_template("survey.html", survey=survey, name=name)

@app.route("/begin/<name>", methods=["POST"])
def begin_survey(name):
    """Initialize an empty 'responses' list in a session and redirect to the first question of the survey"""
    responses = []
    session['responses'] = responses
    return redirect(f"/surveys/{name}/question/0")

@app.route("/surveys/<name>/question/<int:number>")
def question(name, number):
    """Display a question page with question and choices
    
    If the user has completed the survey or tries to answer a question
    out of order, they will be redirected appropriately
    """
    survey = surveys[name]
    survey_complete = request.cookies.get(f"{name}_complete", "")
    responses = session['responses']
    
    # protect route
    if survey_complete:
        flash(f"The {survey.title} has already been completed.", "error")
        return redirect("/") 
    elif not number == len(responses):
        flash("The questions must be completed in order.", "error")
        return redirect(f"/surveys/{name}/question/{len(responses)}")

    question = survey.questions[int(number)]

    """ next_number will show the non-index question number 
    and also give the number of the next question for the link route """
    next_number = number + 1
    return render_template("question.html", survey=survey, question=question, next_number=next_number)

@app.route("/surveys/<name>/question/<int:number>", methods=["POST"])
def question_post(name, number):
    """Handle post request from question page's form
    
    If the final question was answered:
      the user will be redirected to a thank you page

    Otherwise:
      'answer' from post request will be added to session['responses'] list
      and user will be redirected to next question in the survey
    """
    survey = surveys[name]
    
    answer = request.form["answer"]
    
    resp = {}
    # handle if the question had a 2nd part to specify a text answer
    try:
        resp = {"answer": answer, "specify": request.form["specify"] }
    except:
        resp = {"answer": answer }
    
    responses = session['responses']
    responses.append(resp)
    session["responses"] = responses

    next_number = number + 1
    if next_number >= len(survey.questions):
        return redirect(f"/surveys/{name}/thankyou") 
    else:
        return redirect(f"/surveys/{name}/question/{number + 1}")

@app.route("/surveys/<name>/thankyou")
def thankyou(name):
    """Display a thank you page to the user to end the survey
    
    Create a cookie for the current survey to store if a user has completed that survey
    to prevent them from doing the survey again
    
    """
    survey = surveys[name]

    html = render_template("thankyou.html", survey=survey)
    resp = make_response(html)
    resp.set_cookie(f"{name}_complete", "True")

    return resp


