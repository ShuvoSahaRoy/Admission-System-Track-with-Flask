from flask import render_template, url_for,flash,redirect
from main_app import app
from main_app.forms import LoginForm,RegistrationForm
from main_app.models import Users,Departments,Students


@app.route('/',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data=="admin@gmail.com" and form.password.data=="password":
            flash(f'Login succesfull')
            return redirect(url_for('home'))
        else:
            flash(f"Wrong Email or Password")
    return render_template('login.html', title='Login', form=form)


@app.route('/register', methods=['get','post'])
def register():
    form= RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!')
        return redirect('/')
    return render_template('register.html',title='Register',form=form)


@app.route('/reset_password')
def reset_password():
    return render_template('reset_password.html')


@app.route('/home')
def home():
    return render_template('home.html')

