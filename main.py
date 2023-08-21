import os


from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user
from sqlalchemy.exc import SQLAlchemyError
from waitress import serve

import database.repository as repo
from database.models import User
from fill_db import fill_db

load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
db = SQLAlchemy()
login_manager = LoginManager()

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URI")
app.debug = True
app.env = "development"
db.init_app(app)
login_manager.init_app(app)


@app.route("/", strict_slashes=False)
def index():
    quotes = repo.paginate_quotes(db, 1, repo.get_all_quotes(db))
    tags = repo.top_ten_tags(db)
    return render_template('quotes.html', quotes=quotes, tags=tags)


@app.route("/page/<page_num>", strict_slashes=False)
def page(page_num):
    quotes = repo.paginate_quotes(db, int(page_num), repo.get_all_quotes(db))
    tags = repo.top_ten_tags(db)
    return render_template('quotes.html', quotes=quotes, tags=tags)


@app.route("/tag/<tag_name>/page/<page_num>", strict_slashes=False)
def tag_page(tag_name, page_num):
    quotes = repo.paginate_quotes(db, int(page_num), repo.get_quotes_by_tag(db, tag_name))
    tags = repo.top_ten_tags(db)
    return render_template('quotes.html', quotes=quotes, tags=tags, tag_name=tag_name)


@app.route("/author/<author_name>", strict_slashes=False)
def author_page(author_name):
    author_name = author_name.replace('-', ' ')
    author = repo.get_author(db, author_name)
    return render_template('author.html', author=author)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if username and password and confirm_password and password == confirm_password:
            try:
                user = User(login=username, password=password)
                db.session.add(user)
                db.session.commit()
                login_user(user)
                return redirect("/")  # register + login sucsess
            except SQLAlchemyError:
                return redirect("/register")  # name already exists
        return redirect("/")  # password != confirm_password


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).filter(User.id == user_id).first()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        user = db.session.query(User).filter(User.login == username).first()
        if user and user.password == password:
            print('login success')
            login_user(user)
            return redirect("/")
        else:
            print('password incorrect')
            return redirect("/login")


@app.route("/add_quote", methods=['GET', 'POST'])
@login_required
def add_quote():
    if request.method == 'GET':
        all_authors = repo.get_all_authors(db)
        all_tags = repo.get_all_tags(db)
        return render_template('add_quote.html', all_authors=all_authors, all_tags=all_tags)
    else:  # POST
        this_author = request.form.get('author')
        this_quote = request.form.get('description')
        this_tags = request.form.getlist('tags')
        repo.add_quote_db(db, this_author, this_quote, this_tags)
        return redirect('/')


@app.route("/add_author", methods=['GET', 'POST'])
@login_required
def add_author():
    if request.method == 'GET':
        return render_template('add_author.html')
    else:  # POST
        this_fullname = request.form.get('fullname')
        this_born_date = request.form.get('born_date')
        this_born_location = request.form.get('born_location')
        this_description = request.form.get('description')
        repo.add_author_db(db, this_fullname, this_born_date, this_born_location, this_description)
        return redirect('/')


@app.route("/add_tag", methods=['GET', 'POST'])
@login_required
def add_tag():
    if request.method == 'GET':
        return render_template('add_tag.html')
    else:  # POST
        this_tag_name = request.form.get('tag_name')
        repo.add_tag_db(db, this_tag_name)
        return redirect('/')


@app.route("/delete_quotes")
@login_required
def del_all_quotes():
    repo.del_all_records(db)
    return redirect('/')


@app.route("/import_quotes")
@login_required
def import_all_quotes():
    fill_db()
    return redirect('/')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == "__main__":
    serve(app, host="127.0.0.1", port=8000)
