from flask import Flask, request, render_template,  redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, User, db, Feedback
from forms import UserForm, LoginForm, FeedbackForm, DeleteForm
from sqlalchemy.exc import IntegrityError 
from werkzeug.exceptions import Unauthorized

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///flask_feedback_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "chickenzarecool21837"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

connect_db(app)

@app.route('/')
def home_page():
    return redirect('/register')

@app.route('/register', methods=['GET', 'POST'])
def show_register():
    """show a form for registering as a new user"""

    if "username" in session:
        return redirect(f"/users/{session['username']}")

    form = UserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        user = User.register(username, password, email, first_name, last_name)
        
        db.session.add(user)
        db.session.commit()

        session['username'] = user.username
       
        return redirect(f'/users/{user.username}')

    else:
        
        return render_template('register.html', form=form)
        

    

@app.route('/users/<username>')
def show_secrets(username):

    if "username" not in session or username != session['username']:
        raise Unauthorized()

    user = User.query.get(username)
    form = DeleteForm()


    return render_template('secrets.html', user=user, form=form)

@app.route('/login', methods=['GET', 'POST'])
def show_login():
    """show a form for a user to login"""
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username,password)
        if user:
            session['user_id'] = user.id
            return redirect('/secrets')
        else:
            form.username.errors = ['Invalid username/password']


    return render_template('login.html', form=form)
  
@app.route('/logout')
def logout_user():
    session.pop('username')
    return redirect('/')

@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):

    form = FeedbackForm()

    if "username" not in session:
        raise Unauthorized()
        
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback(
            title=title,
            content=content,
            username=username,
        )

        db.session.add(feedback)
        db.session.commit()

        

        return redirect(f'/users/{feedback.username}')

    else:
        user = User.query.get(username)
        return render_template('feedback/new.html', form=form, user=user)

@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):

    if "username" not in session or username != session['username']:
        raise Unauthorized()

    user = User.query.get(username)

    db.session.delete(user)
    db.session.commit()
    session.pop('username')
    return redirect('/login')

@app.route('/feedback/<feedback_id>/update', methods=['GET', 'POST'])
def update_feedback(feedback_id):

    feedback = Feedback.query.get(feedback_id)

    if "username" not in session or feedback.username != session['username']:
        raise Unauthorized()

    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        
        db.session.commit()
        return redirect(f'/users/{feedback.username}')

    return render_template('feedback/edit.html', form=form, feedback=feedback)

@app.route('/feedback/<feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):

    feedback = Feedback.query.get(feedback_id)

    if "username" not in session or feedback.username != session['username']:
        raise Unauthorized()

    form = DeleteForm()

    if form.validate_on_submit():
        db.session.delete(feedback)
        db.session.commit()
    
    return redirect(f'/users/{feedback.username}')




