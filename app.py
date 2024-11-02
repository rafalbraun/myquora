from flask import Flask, render_template, url_for, flash, redirect, request, make_response
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from config import Config
from models import db, bcrypt, User, Post
from forms import CreatePostForm, UpdatePostForm, DeletePostForm
from functools import wraps
from dotenv import load_dotenv
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import uuid
import math
import random
import os
import csv
from flask import jsonify

page_size = 20

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)
app.config['SECRET_KEY'] = 'yoursecretkey'

db.init_app(app)

with app.app_context():
    db.drop_all()
    db.create_all()
    db.session.add(User(id=1,username="test1", email="test1@gmail.com", password=bcrypt.generate_password_hash("test1").decode('utf-8')))
    db.session.add(User(id=2,username="admin", email="admin@gmail.com", password=bcrypt.generate_password_hash("admin").decode('utf-8')))
    db.session.add(Post(id=1,rid=1,pid=1,content="lorem ipsum", created_by_id=1))
    db.session.commit()

@app.route("/posts")
def posts():
    page = db.paginate(db.select(Post).order_by(Post.created_at.asc()), per_page=page_size)
    return render_template("posts.html", pagination=page)

@app.route("/post/<int:id>")
def post(id):
    post = db.session.get(Post, int(id))
    return render_template('post.html', post=post)

@app.route("/user/<int:id>")
def user(id):
    user = db.session.get(User, int(id))
    return render_template('user.html', user=user)

@app.route("/post_create", methods=['GET', 'POST'])
def post_create():
    form = CreatePostForm()
    if form.validate_on_submit():
        post = Post()
        form.populate_obj(post)
        db.session.add(post)
        db.session.commit()
        flash(f'Post has been added.', 'success')
        return redirect(url_for('post', id=post.id))
    return render_template('post_create.html', form=form)

@app.route("/post_update/<int:id>", methods=['GET', 'POST'])
def post_update(id):
    post = Post.query.get_or_404(int(id))
    form = UpdatePostForm(request.form, obj=post)
    if form.validate_on_submit():
        form.populate_obj(post)
        db.session.add(post)
        ## here update rid and pid
        db.session.commit()
        flash(f'Post has been updated.', 'success')
        return redirect(url_for('post', id=post.id))
    return render_template('post_update.html', form=form)

@app.route("/post_delete/<int:id>", methods=['GET', 'POST'])
def post_delete(id):
    post = Post.query.get_or_404(int(id))
    form = DeletePostForm(request.form, obj=post)
    if form.validate_on_submit():
        db.session.delete(post)
        db.session.commit()
        flash(f'Post has been deleted.', 'success')
        return redirect(url_for('posts'))
    return render_template('post_delete.html', form=form)

@app.route("/post_comment/<int:id>", methods=['GET', 'POST'])
def post_comment_or_report(id):
    post = Post.query.get_or_404(int(id))
    return redirect(url_for('post', id=post.id))

@app.errorhandler(404) 
def not_found(e): 
    return render_template("404.html") 

if __name__=="__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)