"""Models for Flask Feedback app."""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()

USER_FIELDS = {
    "username": "",
    "password": "",
    "email": "",
    "first_name": "",
    "last_name": ""
}


def connect_db(app):
    """ Associate the flask application app with SQL Alchemy and
        initialize SQL Alchemy
    """
    db.app = app
    db.init_app(app)


# MODELS
class User(db.Model):
    """ User model for a users table in the flask_feedback database. """

    __tablename__ = "users"

    username = db.Column(db.String(20),
                         primary_key=True)

    password = db.Column(db.Text,
                         nullable=False)

    email = db.Column(db.String(50),
                      unique=True,
                      nullable=False)

    first_name = db.Column(db.String(30),
                           nullable=False)

    last_name = db.Column(db.String(30),
                          nullable=False)

    def __repr__(self):
        """Show user information """

        return f"<User username:{self.username}, password:{self.password[0:15]}..., first_name:{self.first_name}, last_name:{self.last_name}, email:{self.email} >"

    def get_full_name(self):
        """ Return the user full name """

        return f"{self.first_name} {self.last_name}"

    @classmethod
    def register(cls, username, pwd):
        """ Register user w/hashed password and return user object. """

        hashed = bcrypt.generate_password_hash(pwd)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        # return instance of user w/username and hashed pwd
        return cls(username=username, password=hashed_utf8)

    @classmethod
    def authenticate(cls, username, pwd):
        """ Validate that user exists & password is correct.

            Return user object when valid; otherwise return False.
        """

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, pwd):
            # return user instance
            return u
        else:
            return False


class Feedback(db.Model):
    """ Feedback model for a feedback table in the flask_feedback database. """

    __tablename__ = "feedback"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)

    title = db.Column(db.String(100),
                      nullable=False)

    content = db.Column(db.Text,
                        nullable=False)

    username = db.Column(db.String(20),
                         db.ForeignKey('users.username'))

    user = db.relationship("User", backref="comments")

    def __repr__(self):
        """Show feedback information """

        return f"<Feedback id:{self.id}, title:{self.title}, content:{self.content}, username:{self.username} >"


# Helper functions

def db_add_user(user_spec_in):
    """ Adds a user to the users table.

    """

    # print(f"\n\nMODEL db_add_user: user_spec_in = {user_spec_in}", flush=True)

    # Take the values in user_spec_in, move them into user_data and handle strip()
    user_data = {}
    for key in user_spec_in.keys():
        user_data[key] = user_spec_in[key].strip()

    new_user = User.register(user_data["username"], user_data["password"])

    new_user.email = user_data["email"].lower()
    new_user.first_name = user_data["first_name"]
    new_user.last_name = user_data["last_name"]

    try:
        db.session.add(new_user)
        db.session.commit()

        results = {
            "success": True,
            "username": new_user.username,
            "message": {
                "text": f"{new_user.username} was created for {new_user.get_full_name()}.",
                "severity": "okay"
            }
        }

    except IntegrityError as err:

        db.session.rollback()

        results = {"success": False}

        error_msg = err.orig.args[0].lower()
        tests = [("key (username)", "username"), ("key (email)", "email")]
        for (test, field) in tests:
            if (test in error_msg):
                results["message"] = {
                    "text": f"{field} '{user_data[field]}' already exists. Please select a different {field}",
                    "severity": "error"
                }
                return results

        # catch-all incase username or email were not found.
        results["message"] = {
            "text": f"Username '{new_data['username']}' and/or email {new_data['email']} are already used. Please select a different username and/or email.",
            "severity": "error"
        }

        return results

    except:

        db.session.rollback()
        results = {
            "success": False,
            "username": "",
            "message": {
                "text": f"Creation Error: An error of unknown origin occured. '{user_spec_in.username}' was NOT created.",
                "severity": "error"
            }
        }

    return results


def db_add_feedback(feedback_in):
    """ Adds feedback to the feedback table.

    """

    # Take the values in feedback_in, move them into feedback_data and handle strip()
    feedback_data = {}
    errors = []

    for key in feedback_in.keys():
        feedback_data[key] = feedback_in[key].strip()
        if (len(feedback_data[key]) == 0):
            errors.append((key, f"{key} cannot be all spaces"))

    if (len(errors) == 0):

        new_feedback = Feedback(
            title=feedback_data["title"], content=feedback_data["content"], username=feedback_data["username"])

        try:
            db.session.add(new_feedback)
            db.session.commit()

            results = {
                "success": True,
                "messages": [("okay", f"Feedback '{new_feedback.title}' was created.")]
            }

        except:
            # future hook for integrity errors

            db.session.rollback()

            results = {
                "success": False,
                "messages": [("error", f"An error occurred. Feedback '{new_feedback.title}' was NOT created.")]
            }

    else:
        # title and/or content were blank
        results = {
            "success": False,
            "messages": errors
        }

    return results


def db_update_feedback(db_feedback, feedback_in):
    """ Updates a feedback record in the feedback table.

        db_feedback the Feedback database object that was used to prefetch the username.
        feedback in contains the title and content from the form.

    """

    # Take the values in feedback_in, move them into feedback_data and handle strip()
    feedback_data = {}
    errors = []

    for key in feedback_in.keys():
        feedback_data[key] = feedback_in[key].strip()
        if (len(feedback_data[key]) == 0):
            errors.append((key, f"{key} cannot be all spaces"))

    if (len(errors) == 0):

        # we looked up the feedback record in app for the user id confirmation. db_feedback
        #  object was passed into the update function.

        db_feedback.title = feedback_data["title"]
        db_feedback.content = feedback_data["content"]

        try:
            # db.session.add(db_feedback)
            db.session.commit()

            results = {
                "success": True,
                "messages": [("okay", f"Feedback '{db_feedback.title}' was updated.")]
            }

        except:
            # future hook for integrity errors

            db.session.rollback()

            results = {
                "success": False,
                "messages": [("error", f"An error occurred. Feedback '{db_feedback.title}' was NOT updated.")]
            }

    else:
        # title and/or content were blank
        results = {
            "success": False,
            "messages": errors
        }

    return results


def db_delete_feedback(db_feedback):
    """ deletes a feedback record from the feedback table """

    msg_title_hold = db_feedback.title

    db.session.delete(db_feedback)

    try:
        db.session.commit()

        results = {
            "message": ("okay", f"'{msg_title_hold}' was deleted."),
            "successful": True
        }

    except:
        db.session.rollback()

        results = {
            "message": ("error", f"An error occurred. '{msg_title_hold}' was NOT deleted."),
            "successful": False
        }

    return results


def db_delete_user(username):
    """ deletes a user record from the users table and feedback for the user from 
        the feedback table. 
    """

    results = {"messages": []}

    # delete all of username's feedback
    nbr_of_feedbacks = Feedback.query.filter_by(username=username).delete()
    if (nbr_of_feedbacks > 0):
        try:
            db.session.commit()
            if (nbr_of_feedbacks == 1):
                results["messages"].append(
                    ("okay", "1 piece of feedback was deleted."))

            else:
                results["messages"].append(
                    ("okay", f"{nbr_of_feedbacks} pieces of feedback were deleted."))

        except:
            db.session.rollback()
            # An error occurred while deleting x pieces of feedback. Delete of username did NOT occur.
            results["successful"] = False

            if (nbr_of_feedbacks == 1):
                results["messages"].append(
                    ("error", f"An error occurred while deleting 1 piece of feedback. Delete of {username} did NOT occur."))
            else:
                results["messages"].append(
                    ("error", f"An error occurred while deleting {nbr_of_feedbacks} pieces of feedback. Delete of {username} did NOT occur."))

            # return -- user had feedback that could not get deleted. Do not delete the user.
            return results

    # delete username
    User.query.filter_by(username=username).delete()
    try:
        db.session.commit()
        results["successful"] = True
        results["messages"].append(("okay", f"User '{username}' was deleted."))

    except:
        db.session.rollback()
        results["successful"] = False
        results["messages"].append(
            ("error", f"An error occurred while deleting {username}. {username} was NOT deleted."))

    return results
