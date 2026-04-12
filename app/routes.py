from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm,PostFoam
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post
from sqlalchemy import select
from flask import request
from urllib.parse import urlparse
from datetime import datetime, timezone

@app.route('/', methods = ['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])
@login_required
def index():
    form = PostFoam()
    if form.validate_on_submit():
        post = Post(author = current_user, body = form.post.data)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    query = current_user.followed_posts()
    posts = db.paginate(query, page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('index', page = posts.next_num if posts.has_next else None)
    prev_url = url_for('index', page = posts.prev_num if posts.has_prev else None)
    return render_template('index.html', title = 'Home', posts = posts.items, form = form, next_url = next_url, prev_url= prev_url)

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
    form = EmptyForm()
    user_obj = select(User).where(User.username == username)
    user = db.session.scalars(user_obj).one_or_none()
    page = request.args.get('page', 1, type = int)
    query = select(Post).where(User.username == username)
    posts = db.paginate(query, page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('user', user = user.username, page = posts.next_num if posts.has_next else None)
    prev_url = url_for('user', page = posts.prev_num if posts.has_prev else None)
    return render_template('user.html', user = user.username, posts=posts.items, user=user, form=form, next_url= next_url, prev_url= prev_url)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/edit_profile', methods = ['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
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

@app.route('/follow_user/<username>', methods = ['POST'])
@login_required
def follow_user(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(select(User).where(User.username == username))
        if user is None:
            flash(f'{username} not found')
            return redirect(url_for('index'))
        elif user == current_user:
            flash('you cannot follow yourself')
            return redirect(url_for('user', username=user.username))
        current_user.follow(user)
        db.session.commit()
        flash(f'You are now following {user}!')
        return redirect(url_for('user', username = user.username))
    else:
        return redirect(url_for('index'))

@app.route('/unfollow_user/<username>', methods = ['POST'])
@login_required
def unfollow_user(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(select(User).where(User.username == username))
        if user is None:
            flash(f'User not found')
            return redirect(url_for('index'))
        if user == current_user:
            flash(f'You cannot unfollow yourself')
            return redirect(url_for('user', username=user.username))
        current_user.unfollow(user)
        db.session.commit()
        flash(f'You unfollowed {user}')
        return redirect(url_for('user', username=user.username))
    else:
        return redirect(url_for('index'))

@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    query = select(Post).order_by(Post.timestamp.desc())
    posts = db.paginate(query, page = page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('index', page = posts.next_num if posts.has_next else None)
    prev_url = url_for('index', page = posts.prev_num if posts.has_prev else None)
    return render_template('index.html', title = 'Home', posts = posts.items, next_url = next_url, prev_url= prev_url)