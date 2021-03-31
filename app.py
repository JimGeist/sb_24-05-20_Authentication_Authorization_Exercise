""" Flask Feedback app """

from flask import Flask, jsonify, request, redirect, render_template, redirect, flash, session
# from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, USER_FIELDS, db_add_user, db_delete_user
from models import db, connect_db, Feedback, db_add_feedback, db_update_feedback, db_delete_feedback
from config import APP_KEY
from forms import LoginForm, RegistrationForm, FeedbackForm

app = Flask(__name__)

# Flask and SQL Alchemy Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///flask_feedback_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

app.config['SECRET_KEY'] = APP_KEY

# # debugtoolbar
# debug = DebugToolbarExtension(app)
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)


# Form Routes

@app.route("/")
def home_page():
    """ Home page for the Flask Feedback application.
        Redirects to /register
    """

    return redirect("/register")


@app.route("/register", methods=["GET", "POST"])
def create_user_page():
    """ route: /register  Present visitor with a form that lets them create a new user
        by username, password, email, first_name, and last_name, all of which are required.
        username is created when username and email are unique and all fields provided.

        Redirects to /user/username upon successful creation of username.
    """

    form = RegistrationForm()

    if form.validate_on_submit():
        new_user = USER_FIELDS

        new_user["username"] = form.username.data
        new_user["password"] = form.password.data
        new_user["email"] = form.email.data
        new_user["first_name"] = form.first_name.data
        new_user["last_name"] = form.last_name.data

        results = db_add_user(new_user)

        if (results["success"]):

            session["username"] = results["username"]

            # on successful login, redirect to /user/username page
            return redirect(f'/user/{results["username"]}')
        else:
            # FUTURE: move the error to the field error

            flash(results["message"]["text"],
                  f'flash-{results["message"]["severity"]}')
            return render_template("registration.html", form=form)

    else:
        return render_template("registration.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login_user_page():
    """ route: /login  Present visitor with a form that lets them login by providing their
        username and password, email, first_name, and last_name, all of which are required.
        username is created when username and email are unique and all fields provided.

        Redirects to /user/username upon successful login.
    """

    form = LoginForm()

    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data

        # authenticate returns either a user object or False
        auth_user = User.authenticate(username, password)

        if (auth_user):

            session["username"] = auth_user.username

            return redirect(f"/user/{username}")

        else:
            # handle the error messaging better
            flash("username and / or password are incorrect.", "flash-error")

    return render_template("login.html", form=form)


@app.route("/secret", methods=["GET"])
def secret_page():
    """ route: /secret  Restricted page viewable only by authenticated users.
    """

    if ("username" in session):
        return render_template("secret.html")

    return redirect("/login")


@app.route("/user")
def user_limbo():
    """ route: //user  User may be lost. Redirect them to user/<username> when logged in, otherwise 
        redirect them to the login page.
    """

    if ("username" in session):
        return redirect(f"/user/{session['username']}")

    else:
        return redirect("/login")


@app.route("/user/<username>", methods=["GET"])
def view_user_page(username):
    """ route: //user/<username>  Restricted page viewable only by authenticated user.

        Page displays profile details about the user specified by username.

        All of the feedback from user username is displayed on the page and each piece of feedback displayed
        has a link to a form to edit the feedback and a button to delete the feedback.

        Have a link that sends you to a form to add more feedback and a button to delete the user. Make sure 
        that only the user who is logged in can successfully view this page.

    """

    if ("username" in session):
        if (session["username"] == username):
            auth_user = User.query.get_or_404(username)
            full_name = auth_user.get_full_name()

            form = RegistrationForm(obj=auth_user)

            user_feedback = Feedback.query.filter_by(username=username).all()

            return render_template("view_user.html", full_name=full_name,
                                   form=form, form_user=username, feedback=user_feedback)
        else:
            # view of another's profile is not allowed.
            flash("You may only view your profile!", "flash-error")
            return redirect(f"/user/{session['username']}")

    else:
        flash("You must login to view your profile.", "flash-error")

    return redirect("/login")


# POST /users/<username>/delete
# Remove the user from the database and make sure to also delete all of their feedback. Clear any user
# information in the session and redirect to /. Make sure that only the user who is logged in can
# successfully delete their account
@app.route("/user/<username>/delete", methods=["POST"])
def delete_user(username):
    """ route: /user/<username>/delete  Delete the user and all their feedback from the database. 
        User information in the session is cleared (user logged out) and redirected to /. 

        Only the user who is logged in can successfully delete their account.
    """

    if ("username" in session):
        session_username = session["username"]
        if (session_username == username):

            # future code - something to confirm the delete to let the user know they delete will
            #  delete their account and all feedback. It cannot be undone.

            results = db_delete_user(username)

            # flash messages then logout. Up to 2 flash messages may exist - one for the delete of
            #  feedback and one for the delete of the user (if possible).
            for (severity, msg) in results["messages"]:
                flash(msg, f"flash-{severity}")

            if (results["successful"]):
                # deletes were successful. logout

                logout_user()

            else:
                # delete was not successful.

                return redirect(f"/user/{username}")

        else:
            # delete of another's profile is not allowed.
            flash("You may only delete your profile!", "flash-error")
            return redirect(f"/user/{username}")

    else:
        flash("You must login to delete your profile.", "flash-error")

    return redirect("/login")


@app.route("/user/<username>/feedback/add", methods=["GET", "POST"])
def add_user_feedback_page(username):
    """ route: /user/<username>/feedback/add:   Only the logged in user can see their page. 
        Displays a form for the user to add feedback. When feedback is successfully added, the user is
        redirected to /users/<username>
    """

    if ("username" in session):

        form = FeedbackForm()

        if form.validate_on_submit():
            feedback_info = {
                "title": form.title.data,
                "content": form.content.data,
                "username": username
            }

            results = db_add_feedback(feedback_info)

            if (results["success"]):

                flash(results['messages'][0][1],
                      f"flash-{results['messages'][0][0]}")

                return redirect(f"/user/{ username }")
            else:

                # FUTURE: handle the error messaging better by addinbg the messages to the fields error,
                # for now, flash them
                for (field, msg) in results["messages"]:
                    flash(msg, "flash-error")

                return render_template("add_or_update_feedback.html", mode="Add", form=form, username=username)

        else:

            return render_template("add_or_update_feedback.html", mode="Add", form=form, username=username)

    else:
        flash("You must login to provide feedback.", "flash-error")

    return redirect("/login")


@app.route("/logout", methods=["POST"])
def logout_user():
    """ route: /logout  logs user out by removing credentials from session.
        Redirect to login page.

        Trying to hang the logout as a form on the view_user page.

    """

    session.pop("username")

    return redirect("/login")


# GET /feedback/<feedback-id>/update
#     Display a form to edit feedback — **Make sure that only the user who has written that feedback can see this form **
# POST /feedback/<feedback-id>/update
#     Update a specific piece of feedback and redirect to /users/<username> — Make sure that only the user who has written
# that feedback can update it
@app.route("/feedback/<feedback_id>/update", methods=["GET", "POST"])
def update_feedback_page(feedback_id):
    """ route: /feedback/<feedback-id>/update:  Only the user who authored the feedback identified by
        feedback-id can see the update page. 
        Displays a form for the user to update feedback. The user who authored the feedback is the only person
        who can update the feedback.
        Only logged in users can perform an update to feedback.
        Form redirects to /users/<username> after the update.
        Form redirects to /login when the a user is not logged in.
    """

    if ("username" in session):

        # user is logged in, but did they write the feedback?

        db_feedback = Feedback.query.get_or_404(feedback_id)
        session_username = session["username"]

        if (db_feedback.username == session_username):

            form = FeedbackForm(obj=db_feedback)

            if form.validate_on_submit():
                feedback_info = {
                    "title": form.title.data,
                    "content": form.content.data
                }

                results = db_update_feedback(db_feedback, feedback_info)

                if (results["success"]):

                    flash(results['messages'][0][1],
                          f"flash-{results['messages'][0][0]}")

                    return redirect(f"/user/{ session_username }")
                else:

                    # FUTURE: handle the error messaging better by addinbg the messages to the fields error,
                    # for now, flash them
                    for (field, msg) in results["messages"]:
                        flash(msg, "flash-error")

                    return render_template("add_or_update_feedback.html", mode="Update", form=form, username=session_username)

            else:
                # return render_template("add_or_update_feedback.html", mode="Update", form=form)
                return render_template("add_or_update_feedback.html", mode="Update", form=form, username=session_username)

        else:
            # feedback_id does not belong to this user.
            flash("You cannot edit another users feedback.", "flash-error")

            return redirect(f"/user/{ session_username }")

    else:
        flash("You must login to update feedback.", "flash-error")

    return redirect("/login")


@app.route("/feedback/<feedback_id>/delete", methods=["GET", "POST"])
def delete_user_feedback(feedback_id):
    """ route: /feedback/<feedback_id>/delete:  Delete feedback associated with feedback_id. Only a logged in user 
        can delete their own feedback. A user cannot delete another user's feedback.

        redirected to /users/<username>
    """

    if ("username" in session):
        session_username = session["username"]

        # user is logged in, but did they write the feedback?

        db_feedback = Feedback.query.get(feedback_id)

        if (db_feedback):

            if (db_feedback.username == session_username):

                results = db_delete_feedback(db_feedback)

                flash(results['message'][1], f"flash-{results['message'][0]}")

            else:
                # feedback_id does not belong to this user.
                flash("You cannot delete another users feedback.", "flash-error")

        else:
            # feedback_id does not exist.
            flash(
                "The requested feedback was not found and was NOT deleted.", "flash-error")

        return redirect(f"/user/{ session_username }")

    else:
        flash("You must login to delete your feedback.", "flash-error")

    return redirect("/login")
