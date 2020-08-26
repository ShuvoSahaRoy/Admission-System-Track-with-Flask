from flask import render_template, url_for, flash, redirect,request
from main_app import app,db,mail
from main_app.forms import LoginForm, RegistrationForm, RequestResetForm, ResetPasswordForm, StudentForm,SearchForm
from passlib.hash import sha256_crypt
from main_app.models import Users, Departments, Students
from flask_login import login_user,current_user,logout_user,login_required
from flask_mail import Message
from PIL import Image
import os,secrets


@app.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/home')
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
    if current_user.is_authenticated:
        return redirect('/home')
    form = RegistrationForm()
    if form.validate_on_submit():
        password = sha256_crypt.encrypt(str(form.password.data))
        user = Users(username=form.username.data, email=form.email.data, password=password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!')
        return redirect('/')
    return render_template('register.html', title='Register', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@app.route('/home',methods=['GET','POST'])
def home():
    if request.method=="POST":
        name = request.form.get('search_box')
        if name!= "":
            student = Students.query.filter_by(name=name).first()
            if student:
                image_file = url_for('static', filename='img/' + student.image_file)
                return render_template('student_profile.html',student = student,image=image_file)
            else:
                flash('Whoops! Student not found.')
                return redirect('/home')
        else:
            flash('Search Box is empty.')

    if current_user.is_authenticated:
        students = Students.query.order_by(Students.admission_num.desc()).all()
        return render_template('home.html',students = students)
    else:
        flash(f"You have to Login First.")
        return redirect('/')


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link: 
    {url_for('reset_token', token=token, _external=True)}
    If you did not make this request then simply ignore this email and no changes will be made.
    '''
    mail.send(msg)


@app.route("/reset_password",methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("An email has been sent with instruction to reset your password.",'info')
        return redirect('/')
    return render_template('reset_request.html',title= 'Reset Password', form= form)


@app.route("/reset_password/<token>",methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = Users.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token','warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = sha256_crypt.encrypt(str(form.password.data))
        user.password = hashed_password
        db.session.commit()
        flash(f'Password reset successful! Now you are able to log in.','success')
        return redirect('/login')
    return render_template('reset_token.html',title= 'Reset Password', form=form)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _,f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex+ f_ext
    picture_path = os.path.join(app.root_path,'static/img',picture_fn)
    output_size= (225,225)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


# total_seat = {'CSTE': 0, 'ACCE': 0, 'ICE': 0, 'EEE': 0, 'SE': 0, 'AM': 0}
#
# def student(dept):
#     for key in total_seat.keys():
#         if key == dept:
#             total_seat[key] = total_seat[key] + 1
#         if total_seat['CSTE'] > 2:
#             return False
#         elif total_seat['ICE'] > 30:
#             return False
#     return total_seat

@app.route("/student_info",methods=['GET','POST'])
@login_required
def student():
    form = StudentForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            entry = Students(id = form.id.data,name=form.name.data,email=form.email.data,image_file=picture_file,
                               department=form.department.data)
        else:
            entry = Students(id=form.id.data, name=form.name.data, email=form.email.data,department=form.department.data)

        db.session.add(entry)
        db.session.commit()
        flash(f'{form.name.data} added as a student!')
        return redirect('/home')
    return render_template('student_info.html', title='Student', form=form)


@app.route("/update/<int:admission_id>",methods=['GET','POST'])
@login_required
def update_info(admission_id):
    student = Students.query.get_or_404(admission_id)
    image_file = url_for('static', filename='img/' + student.image_file)
    form = StudentForm()
    if form.validate_on_submit():
        student.id = form.id.data
        student.name = form.name.data
        student.email = form.email.data
        student.department = form.department.data
        if form.picture.data:
            student.image_file = save_picture(form.picture.data)
        db.session.commit()
        flash(f'{form.name.data}\'s info updated successfully!')
        return redirect('/home')
    elif request.method == 'GET':
        form.id.data = student.id
        form.name.data = student.name
        form.email.data = student.email
        form.department.data = student.department
        return render_template('update.html',form=form,image=image_file)
    return render_template('update.html',form=form,image=image_file)


@app.route('/delete/<int:admission_id>', methods=["POST","GET"])
@login_required
def delete_student(admission_id):
    student = Students.query.get_or_404(admission_id)
    db.session.delete(student)
    db.session.commit()
    flash('Student details has been Deleted!', 'success')
    return redirect('/home')


@app.route('/home/<string:profile>')
@login_required
def profile(profile):
    student = Students.query.filter_by(name=profile).first()
    image_file = url_for('static', filename='img/' + student.image_file)
    return render_template('student_profile.html', student=student, image=image_file)
