from flask import render_template, url_for, flash, redirect
from main_app import app,db
from main_app.forms import LoginForm, RegistrationForm
from passlib.hash import sha256_crypt
from main_app.models import Users, Departments, Students
from flask_login import login_user,current_user,logout_user,login_required


@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user and sha256_crypt.verify(form.password.data,user.password):
            login_user(user, remember=form.remember.data)
            flash(f'Login succesfull')
            return redirect(url_for('home'))
        else:
            flash(f"Wrong Email or Password")
    return render_template('login.html', title='Login', form=form)


@app.route('/register', methods=['get', 'post'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        password = sha256_crypt.encrypt(str(form.password.data))
        user = Users(username=form.username.data, email=form.email.data, password=password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!')
        return redirect('/')
    return render_template('register.html', title='Register', form=form)


@app.route('/reset_password')
def reset_password():
    return render_template('reset_password.html')


@app.route('/home')
def home():
    return render_template('home.html')
