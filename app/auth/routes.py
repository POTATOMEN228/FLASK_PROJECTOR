from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User
from app.forms import ProfileForm, RegisterForm, LoginForm
import os
from werkzeug.utils import secure_filename
from flask import current_app

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter(
            (User.username == form.username.data) | (User.email == form.email.data)
        ).first()
        if existing_user:
            flash('A user with that name or email already exists.')
            return redirect(url_for('auth.register'))
        
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Now log in.')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            flash('You are logged in!')
            return redirect(url_for('main.home'))
        else:
            flash('You entered your data incorrectly or you do not have an account.')
            return redirect(url_for('auth.login'))
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out of your account.')
    return redirect(url_for('main.home'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        flash('First, log in to your account.')
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])
    form = ProfileForm(obj=user)

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.about_me = form.about_me.data

        if form.profile_image.data:
            filename = secure_filename(form.profile_image.data.filename)
            image_path = os.path.join('app', 'static', 'uploads', filename)
            form.profile_image.data.save(image_path)
            user.profile_image = filename

        db.session.commit()
        flash('Profile updated.')
        return redirect(url_for('auth.profile'))

    # фильтрация рецептов я переместил
    query = user.recipes

    search = request.args.get('q')
    category = request.args.get('category')

    if search:
        query = [r for r in query if search.lower() in r.title.lower()]
    if category:
        query = [r for r in query if r.category == category]

    return render_template('profile.html', form=form, user=user, recipes=query, search=search, category=category)
