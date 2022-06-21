# Import Libraries

import os
import random
from flask import Flask, render_template,redirect, request, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from validate_email import validate_email
from flask_login import login_required, UserMixin, login_user, logout_user, LoginManager, current_user
from flask_session import Session
from flask_mail import Mail, Message
from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.


# Sign in form

class Signinform(FlaskForm):
    username = StringField(label = "Enter username")
    email = StringField(label = "Input a valid Email Id")
    password1 = PasswordField(label="Password")
    password2 = PasswordField(label="Confirm Password")
    submit = SubmitField(label="Submit")

# Login Form

class Loginform(FlaskForm):
    username = StringField(label="Enter your username")
    password = PasswordField(label="Enter password")
    submit = SubmitField(label="Login")

# ResetPassword form

class Reset(FlaskForm):
    gmail = StringField(label="Gmail Id")
    code = IntegerField(label="Enter the code here")
    submit = SubmitField()


# App name declaration
app = Flask(__name__)

mail = Mail(app) # instantiate the mail class


# Session configuration
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Mail configurations

   
# configuration of mail
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.getenv('sender')
app.config['MAIL_PASSWORD'] = os.getenv('password')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)




# Database confiugrations

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market.db'
app.config['SECRET_KEY'] = os.getenv('secret_key')
db = SQLAlchemy(app)

# login required

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# database tables

# User tables created as columns with sqlalchemy, created from terminal window

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer(), nullable=False, unique=True, primary_key=True)
    username = db.Column(db.String(length=34), unique=True, nullable=False)
    password = db.Column(db.String(length=60), nullable=False)
    email = db.Column(db.String(), nullable=False, unique = True)
    items = db.relationship('Items', backref="owned_user", lazy=True)
    scores = db.relationship('Scores', backref="owned_user", lazy=True)

# Items table to store information on each items

class Items(db.Model):
    product = db.Column(db.String(), nullable=False)
    price = db.Column(db.String(), nullable=False)
    id = db.Column(db.Integer(), nullable=False, unique=True, primary_key=True)
    owner = db.Column(db.Integer(), db.ForeignKey('users.id'))

# Scores table to store top scorer, leaderboard.etc.
class Scores(db.Model):
    id = db.Column(db.Integer(), primary_key = True)
    user = db.Column(db.Integer(), db.ForeignKey('users.id'))
    rank = db.Column(db.Integer(), nullable=False, default = 0)
    budget = db.Column(db.Integer(), nullable = False, default = 1000)
    spent = db.Column(db.Integer(), nullable = False, default = 0)
    lost = db.Column(db.Integer(), nullable = False, default = 0)
    name = db.Column(db.String(length=34), unique=True, nullable=False)

# Routes


@app.route('/')
@app.route('/home')
def index():
    if session.get("login"):
        reply = False
    else:
        reply = True
    return render_template("index.html", loggedin = reply)


@app.route('/about')
@login_required
def about():
    ite = Scores.query.order_by(Scores.budget.desc()).all()
    return render_template('about.html', items=ite)

@app.errorhandler(404)
def resource_not_found(e):
    return render_template('error.html')

@app.errorhandler(500)
def resource_not_found(e):
    return render_template('error.html')

@app.route('/sign-in', methods=["GET", "POST"])
def sign():
    form = Signinform()
    if request.method == "POST":

        if form.validate_on_submit():
            message = check_username(form.username.data)
            if message != "":
                return render_template('signin.html', form = form, message = message)
            is_valid = validate_email(form.email.data)
            if is_valid == False:
                message2 = "Your Email is not valid"
                return render_template('signin.html', form = form, message= message2)
            check_mail_exist = Users.query.filter_by(email = form.email.data).first()
            if check_mail_exist != None:
                message3 = "Email already exists"
                return render_template('signin.html', form = form, message = message3)
            message4 = check_password(form.password1.data, form.password2.data)
            if message4 != "":
                return render_template('signin.html',form = form, message = message4)
            user_data = Users(username = form.username.data,
            email = form.email.data, password = form.password2.data)
            db.session.add(user_data)
            db.session.commit()
            s = Scores(name = form.username.data)
            s.owner =  Users.query.filter_by(username=form.username.data).first().id
            db.session.add(s)
            db.session.commit()
            session["login"] = True
            session["user"] = form.username.data
            session["mail"] = form.email.data
            msg = Message(
                            'Welcome to Manage',
                            sender = os.getenv('sender'),
                            recipients = [form.email.data]
                        )
            msg.body = 'Hello, Welcome to Manage, you are logged in as ' + form.username.data +'. We will be notifying through gmail important checkpoints as we move forward to the game'
            mail.send(msg)

            login_user(Users.query.filter_by(username = form.username.data).first())
            return redirect(url_for('about'))
    else:
        return render_template('signin.html', form=form)

@app.route('/log-in', methods=['GET', 'POST'])
def login():
    form = Loginform()
    if request.method == 'POST':
        # todo
        if form.validate_on_submit():
            user = form.username.data
            passcode = form.password.data
            check_username = Users.query.filter_by(username = user).first()
            if check_username == None:
                message = "Username doesn't exist"
                return render_template('login.html',form=form, msg = message)
            check_pass = Users.query.filter_by(username = user).first().password
            if passcode != check_pass:
                message2 = "Your Passwords dont match"
                return render_template("login.html", form=form, msg2=message2)
            
            session["login"] = True
            session["user"] = form.username.data
            login_user(Users.query.filter_by(username = user).first())
            msg = Message(
                'Somebody logged into your account',
                sender = os.getenv('sender'),
                recipients = [Users.query.filter_by(username=form.username.data).first().email]
            )
            msg.body = "Somebody logged into your account, if it's you, then you can ignore this email"
            mail.send(msg)
            return redirect(url_for('about'))        
    else:
        return render_template('login.html', form = form)


def check_username(name):
    if len(name) > 34:
        return "Name too long"
    if len(name) < 2:
        return "Name too short"
    if " " in name:
        return "Name should not container blank characters"
    item = Users.query.all()
    for items in item:
        if items.username == name:
            return "Username already exists"
    return ""

def check_password(pass1, pass2):
    if len(pass1) < 8:
        return "Password length too short"   
    if pass1 != pass2:
        return "Passwords don't match"
    return ""



@app.route('/logout', methods=["GET", "POST"])
@login_required
def logout():
    session["login"] = False
    Users.query.filter_by(username = session["user"]).delete()
    session["user"] = None
    db.session.commit()
    logout_user()
    return redirect(url_for('index'))


@app.route('/buy', methods=["GET", "POST"])
@login_required
def buy():
    # Todo
    return "BUY"

@app.route('/sell', methods=["GET", "POST"])
@login_required
def sell():
    # Todo
    return "Sell"


@app.route('/resetpassword', methods=["GET", "POST"])
def forgotpassword():
    form = Reset()
    if request.method == 'POST':
        # todo
        fdata = Users.query.filter_by(email = form.gmail.data).first()
        if fdata == None:
            info = "Sorry we couldn't find your email, We suggest going back and sign-up for a new account"
            return render_template('forgot.html', form=form, info=info)
        random_no = random.randint(100000, 999999)
        msg = Message(
            'Password Reset',
            sender = os.getenv('sender'),
            recipients = [form.gmail.data]
        )
        msg.body = "Your code to reset your password is " + str(random_no) + ". Please note that this code will expire in a few minutes. Please copy and paste the code in the input field"
        mail.send(msg)
        session['code'] = random_no
        session["mail"] = form.gmail.data
        # return redirect(f"/updatepassword/{session['code']}")
        # Ensuring security
        return redirect(url_for("updatepassword", code = session['code'] + random.randint(100000, 999999) + random.randint(100000, 999999)))
    else:
        return render_template('forgot.html', form=form)


@app.route('/updatepassword/<int:code>', methods=["GET", "POST"])
def updatepassword(code):
    if not session.get('code' or  code != session['code']):
        return redirect(url_for('forgotpassword'))
    form = Reset()
    if request.method == "POST":
        if session["code"] != form.code.data:
            info = "Incorrect code"
            return render_template('update.html', form = form, info = info)
        # return redirect(f"/update2/{session['code']}")
        return redirect(url_for("update2", code = session['code']))

    else:
        return render_template('update.html', form= form)

@app.route("/update2/<int:code>", methods=["GET", "POST"])
def update2(code):
    if not session.get('code') or code != session['code']:
        return redirect(url_for("forgotpassword"))
    form = Signinform()
    if request.method == "POST":
        id = form.password1.data
        mailid = session["mail"]
        Users.query.filter_by(email = mailid).first().password = id 
        db.session.commit()
        return redirect(url_for('about'))
    else:
        return render_template("update2.html", form = form)