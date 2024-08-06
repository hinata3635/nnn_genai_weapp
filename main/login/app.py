
from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Optional
from datetime import datetime, timedelta
import os
import random
import string

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=30)
app.permanent_session_lifetime = timedelta(days=30)

# Flask-Loginの初期化
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
db = SQLAlchemy(app)

# Userモデルの定義 (UserMixinを継承)
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(db.String(10), unique=True, nullable=False)
    mail = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    group_code = db.Column(db.String(8), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def create_new_user(cls, mail, password, name, group_code):
        unique_id = cls.generate_unique_id()
        existing_user = cls.query.filter_by(mail=mail).first()
        if existing_user is not None:
            return None
        new_user = cls(unique_id=unique_id, mail=mail, name=name, group_code=group_code)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    @classmethod
    def generate_unique_id(cls, length=10):
        characters = string.ascii_letters + string.digits
        while True:
            unique_id = ''.join(random.choice(characters) for _ in range(length))
            if not cls.query.filter_by(unique_id=unique_id).first():
                return unique_id

# Groupモデルの定義 (UserMixinを継承)
class Group(UserMixin, db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    unique_code = db.Column(db.String(8), unique=True, nullable=False)
    mail = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(64), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def create_new_group(cls, mail, password, name):
        unique_code = cls.generate_unique_code()
        existing_group = cls.query.filter_by(mail=mail).first()
        if existing_group is not None:
            return None
        new_group = cls(unique_code=unique_code, mail=mail, name=name)
        new_group.set_password(password)
        db.session.add(new_group)
        db.session.commit()
        return new_group

    @classmethod
    def generate_unique_code(cls, length=8):
        characters = string.ascii_letters + string.digits
        while True:
            unique_code = ''.join(random.choice(characters) for _ in range(length))
            if not cls.query.filter_by(unique_code=unique_code).first():
                return unique_code

# Flask-Login用のユーザーローダー関数
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ログインフォームの定義
class LoginForm(FlaskForm):
    mail = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# 登録フォームの定義
class RegistrationForm(FlaskForm):
    mail = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    name = StringField('Name', validators=[DataRequired()])
    group_code = StringField('Group Code', validators=[Optional()])
    submit = SubmitField('Register')

# グループログインフォームの定義
class AuthorLoginForm(FlaskForm):
    mail = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# グループ登録フォームの定義
class AuthorRegistrationForm(FlaskForm):
    mail = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Register')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(mail=form.mail.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            flash('Login Successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('chachat'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User.create_new_user(
            mail=form.mail.data,
            password=form.password.data,
            name=form.name.data,
            group_code=form.group_code.data if form.group_code.data else ""
        )
        if new_user:
            flash('Registration Successful! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Email already exists. Please choose a different one.', 'danger')
    return render_template('register.html', title='Register', form=form)

@app.route('/author_login', methods=['GET', 'POST'])
def author_login():
    form = AuthorLoginForm()
    if form.validate_on_submit():
        group = Group.query.filter_by(mail=form.mail.data).first()
        if group and group.check_password(form.password.data):
            login_user(group, remember=True)
            flash('Login Successful!', 'success')
            return redirect(url_for('login'))  # login.html にリダイレクト
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('author_login.html', title='Author Login', form=form)

@app.route('/author_register', methods=['GET', 'POST'])
def author_register():
    form = AuthorRegistrationForm()
    if form.validate_on_submit():
        new_group = Group.create_new_group(
            mail=form.mail.data,
            password=form.password.data,
            name=form.name.data
        )
        if new_group:
            flash('Registration Successful! Please log in.', 'success')
            return redirect(url_for('author_login'))
        else:
            flash('Email already exists. Please choose a different one.', 'danger')
    return render_template('author_register.html', title='Author Register', form=form)

@app.route('/chachat')
def chachat():
    return render_template('chachat.html', title='chachat_main')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
def index():
    return render_template("index.html")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=80, debug=False)
