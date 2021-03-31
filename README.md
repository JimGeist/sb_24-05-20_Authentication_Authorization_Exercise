# sb_24-05-20_Authentication_Authorization_Exercise


## Assignment Details
Flask Feedback assignment involved creation of a user feedback system that include authentication, saved encrypted passwords, and authorization safeguards using Python, Flask, SQL Alchemy, and Bcrypt. 

Only authenticated users have the ability to create, update, and delete feedback that *they* created. An authenticated user **must not** not have the ability to see, edit, or delete another user's feedback. The authenticated user can delete themselves, and the delete will also remove all feedback created by the user.

Add, update and delete functions are in model.py. No unittests or doctests,

Flask toolbar debugging statements were included but are commented out.
```sh
# from flask_debugtoolbar import DebugToolbarExtension
    . . . .
# debug = DebugToolbarExtension(app)```
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
```

- The database name is ```flask_feedback_db```  
- The test database name is ```flask_feedback_test_db```


### ENHANCEMENTS
- Messages and error handling. 


### DIFFICULTIES 
- These assignments would be easier for me if I just dropped error checking. I was making good time until Part 8!



