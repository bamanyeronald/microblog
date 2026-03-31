from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from sqlalchemy import select
from flask import request
from urllib.parse import urlparse
from datetime import datetime

@app.route('/')
@app.route('/index')
@login_required
def index():
    user = {'username': 'Miguel'}
    posts = [
        {
            'author':{'username': 'John'},
            'body': 'A beautiful day in Portland'
        },
        {
            'author':{'username': 'Susan'},
            'body': 'The Avengers movie was cool'
        }
    ]
    return render_template('index.html', title = 'Home', posts = posts)

@app.route('/login', methods = ["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        stnt = select(User).where(User.username == form.username.data)
        user = db.session.scalar(stnt)
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc !='':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title = 'Sign in', form = form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username = form.username.data, email = form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations')
        return redirect(url_for('login'))
    return render_template('register.html', title = 'Register', form = form )

@app.route('/user/<username>')
@login_required
def user(username):
    user_obj = select(User).where(User.username == username)
    user = db.session.execute(user_obj).scalar_one_or_none()
    posts = [
        {'author': user, 'body': 'Test_post 1'},
        {'author': user, 'body': 'Test_post 2'}
    ]
    return render_template('user.html', posts = posts, user = user)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/edit_profile', methods = ['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash("Your changes have been saved")
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form = form)