from flask import (
    Flask,
    render_template,
    redirect,
    flash,
    url_for,
    session
)

from datetime import timedelta
from sqlalchemy.exc import (
    IntegrityError,
    DataError,
    DatabaseError,
    InterfaceError,
    InvalidRequestError,
)
from werkzeug.routing import BuildError

from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash

from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    current_user,
    logout_user,
    login_required,
)

from app import create_app, db, login_manager, bcrypt
from models import User
from forms import login_form, register_form
from flask import Flask, flash, request, redirect, url_for, render_template
import urllib.request
import os
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from base64 import b64encode
import base64
from io import BytesIO  # Converts data from Database into bytes

# Flask
from flask import Flask, render_template, request, flash, redirect, url_for, \
    send_file  # Converst bytes into a file for downloads

# FLask SQLAlchemy, Database
from flask_sqlalchemy import SQLAlchemy

basedir = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data.sqlite')

app = Flask(__name__)
app = create_app()
app.config['SQLALCHEMY_DATABASE_URI'] = basedir
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev'
db = SQLAlchemy(app)

class FileContent(db.Model):


    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)
    rendered_data = db.Column(db.Text, nullable=False)
    text = db.Column(db.Text)
    location = db.Column(db.String(64))
    pic_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'Pic Name: {self.name} Data: {self.data} text: {self.text} created on: {self.pic_date} location: {self.location}'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
def load_user(information_id):
    return User.query.get(int(information_id))




UPLOAD_FOLDER = 'static/uploads/'

app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS







@app.before_request
def session_handler():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=1)

@app.route("/index", methods=("GET", "POST"), strict_slashes=False)
@app.route('/')
def index():
    return render_template("index.html", title="Home")


@app.route("/indaa", methods=['GET', 'POST'])
@app.route('/indaa')
def indaa():
    pics = FileContent.query.all()
    if pics:  # This is because when you first run the app, if no pics in the db it will give you an error
        all_pics = pics
        if request.method == 'POST':
            flash('Upload succesful!')


        return render_template('indaa.html', all_pic=all_pics)
    else:
        return render_template('indaa.html')


@app.route('/query')
def query():
    all_pics = FileContent.query.all()
    return render_template('query.html', all_pic=all_pics)


# Render the pics
def render_picture(data):
    render_pic = base64.b64encode(data).decode('ascii')
    return render_pic


# Upload
@app.route('/', methods=['POST'])
def upload():
    pics = FileContent.query.all()
    file = request.files['inputFile']
    data = file.read()
    render_file = render_picture(data)
    text = request.form['text']
    location = request.form['location']

    newFile = FileContent(name=file.filename, data=data, rendered_data=render_file, text=text, location=location)
    db.session.add(newFile)
    db.session.commit()
    full_name = newFile.name
    full_name = full_name.split('.')
    file_name = full_name[0]
    file_type = full_name[1]
    file_date = newFile.pic_date
    file_location = newFile.location
    file_render = newFile.rendered_data
    file_id = newFile.id
    file_text = newFile.text

    return render_template('upload.html', file_name=file_name, file_type=file_type, file_date=file_date,
                           file_location=file_location, file_render=file_render, file_id=file_id, file_text=file_text)
    if pics:  # This is because when you first run the app, if no pics in the db it will give you an error
        all_pics = pics
        if request.method == 'POST':
            flash('Upload succesful!')


        return render_template('indaa.html', all_pic=all_pics)
    else:
        return render_template('indaa.html')
    return redirect(url_for('indaa'))


# Download
@app.route('/download/<int:pic_id>')
def download(pic_id):
    file_data = FileContent.query.filter_by(id=pic_id).first()
    file_name = file_data.name


# Show Pic
@app.route('/pic/<int:pic_id>')
def pic(pic_id):
    get_pic = FileContent.query.filter_by(id=pic_id).first()

    return render_template('pic.html', pic=get_pic)


# Update
@app.route('/update/<int:pic_id>', methods=['GET', 'POST'])
def update(pic_id):
    pic = FileContent.query.get(pic_id)

    if request.method == 'POST':
        pic.location = request.form['location']
        pic.text = request.form['text']
        db.session.commit()



@app.route("/login/", methods=("GET", "POST"), strict_slashes=False)
def login():
    form = login_form()

    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            if check_password_hash(user.pwd, form.pwd.data):
                login_user(user)
                return redirect(url_for('indaa'))
            else:
                flash("Invalid Username or password!", "danger")
        except Exception as e:
            flash(e, "danger")

    return render_template("auth.html",
                           form=form,
                           text="Login",
                           title="Login",
                           btn_action="Login"
                           )


# Register route
@app.route("/register/", methods=("GET", "POST"), strict_slashes=False)
def register():
    form = register_form()
    if form.validate_on_submit():
        try:
            email = form.email.data
            pwd = form.pwd.data
            username = form.username.data
            information = form.information.data

            newuser = User(
                username=username,
                information=information,
                email=email,
                pwd=bcrypt.generate_password_hash(pwd),
            )

            db.session.add(newuser)
            db.session.commit()
            flash(f"Account Succesfully created", "success")
            return redirect(url_for("login"))

        except InvalidRequestError:
            db.session.rollback()
            flash(f"Something went wrong!", "danger")
        except IntegrityError:
            db.session.rollback()
            flash(f"User already exists!.", "warning")
        except DataError:
            db.session.rollback()
            flash(f"Invalid Entry", "warning")
        except InterfaceError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except DatabaseError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except BuildError:
            db.session.rollback()
            flash(f"An error occured !", "danger")
    return render_template("auth.html",
                           form=form,
                           text="Create account",
                           title="Register",
                           btn_action="Register account"
                           )


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/delete/<int:pic_id>')
def delete(pic_id):
    del_pic = FileContent.query.get(pic_id)
    db.session.delete(del_pic)
    db.session.commit()
    flash('Picture deleted from Database')
    return redirect(url_for('indaa'))

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)