from flask import Flask, render_template, url_for, flash, redirect, request, make_response, jsonify, abort
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from config import Config
from models import db, bcrypt, User, Post, Report, Notification
from forms import CreatePostForm, UpdatePostForm, DeletePostForm, CreateCommentForm, ReportPostForm, LoginForm
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

from datetime import datetime, timedelta
from collections import defaultdict
from myutils import build_post_hierarchy, truncate_text_by_word

page_size = 20

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

with app.app_context():
    db.drop_all()
    db.create_all()
    db.session.add(User(id=1,username="test1", email="test1@gmail.com", password=bcrypt.generate_password_hash("test1").decode('utf-8')))
    db.session.add(User(id=2,username="admin", email="admin@gmail.com", password=bcrypt.generate_password_hash("admin").decode('utf-8')))
    db.session.add(Post(id=1,rid=1,pid=1,level=0,created_by_id=1,content="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed et mollis eros, nec commodo metus. Ut ligula orci, elementum sodales neque eget, imperdiet dapibus justo. Nunc consectetur, elit sit amet tempus feugiat, lectus odio rutrum metus, in convallis felis lacus non ipsum. Ut in arcu eu libero fermentum bibendum lobortis vehicula lectus. Vivamus quis ultricies elit. In venenatis ligula enim, vitae interdum leo bibendum nec. Praesent convallis ornare ex, ut tristique quam porta vitae. Sed euismod justo in quam varius rhoncus. Maecenas id sem nec urna mollis aliquet.", comments=3))
    db.session.add(Post(id=2,rid=1,pid=1,level=1,created_by_id=2,content="Suspendisse sapien odio, efficitur id rhoncus a, porttitor ut ante. Sed laoreet libero at nulla dictum, ac ultrices nunc commodo. Sed odio libero, accumsan sit amet nunc eu, feugiat dictum neque. Donec iaculis neque imperdiet nulla auctor tristique. Nullam quis lectus imperdiet, cursus elit ac, ultrices arcu. In condimentum elit et ligula euismod dignissim. Vivamus sed dapibus urna."))
    db.session.add(Post(id=3,rid=1,pid=1,level=1,created_by_id=2,content="Ut id aliquet nibh. In sit amet finibus massa. Aenean imperdiet nisi ut est sagittis vulputate. Duis vestibulum ligula in gravida mattis. Integer gravida tempus vestibulum. Vestibulum placerat pulvinar mi, id dictum quam accumsan id. Suspendisse nec blandit magna. Vivamus ullamcorper, neque mollis rutrum semper, quam justo porta erat, sit amet fermentum libero erat eleifend lorem. Mauris luctus nisl et tortor bibendum, id facilisis arcu auctor. Etiam id euismod massa, et varius ipsum. Nullam sagittis velit at libero feugiat consequat. Donec luctus sapien eu felis pellentesque elementum. Fusce et dolor sed libero tincidunt hendrerit. Donec egestas faucibus justo non consectetur."))
    db.session.add(Post(id=4,rid=1,pid=2,level=2,created_by_id=2,content="Integer sagittis dapibus interdum. Donec est ipsum, volutpat a lacinia eu, dictum vitae dui. Morbi massa sapien, sodales quis ex vel, hendrerit commodo sapien. Curabitur finibus enim vitae quam varius sagittis. Sed sagittis convallis tellus quis semper. Aenean elit nulla, mollis quis tempus in, rhoncus suscipit libero. Morbi nec eros bibendum, vulputate risus eget, accumsan purus. In finibus feugiat est ut sagittis. Fusce quis vehicula odio, vel maximus risus. Nam quis convallis arcu, suscipit lobortis risus. In sit amet commodo risus, vitae mattis turpis. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Aliquam molestie augue magna, sit amet rhoncus lectus venenatis id. Vestibulum eget tristique ex."))
    db.session.commit()

@login_manager.user_loader
def loader_user(user_id):
    return db.session.get(User, int(user_id))

@app.route("/", methods=["GET", "POST"])
def index():
    return redirect(url_for("posts"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated is True:
        return redirect(url_for("posts"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for("posts"))
        else:
            flash(f'Wrong credentials or no such user', 'error')
    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(request.referrer or url_for('default_route'))

@app.route("/posts")
def posts():
    page = db.paginate(db.select(Post).where(Post.id==Post.rid).order_by(Post.created_at.asc()), per_page=page_size)
    for post in page.items:
        post.display_content = truncate_text_by_word(post.content, 120)
    return render_template("posts.html", pagination=page)

@app.route("/post/<int:id>", methods=['GET', 'POST'])
def post(id):
    posts = Post.query.filter_by(rid=id).all()
    if not posts:
        abort(404)

    hierarchy = build_post_hierarchy(posts)
    root=hierarchy[0]

    form1 = CreateCommentForm()
    form2 = ReportPostForm()

    if form1.submit1.data and form1.validate_on_submit():
        ## check if logged in
        if current_user.is_authenticated is False:
            return redirect(url_for("login"))
        post = Post()
        form1.populate_obj(post)
        post.created_by_id = current_user.id

        parent = Post.query.filter_by(id=form1.pid.data).first()
        post.level = parent.level+1
        root.comments = root.comments+1
        db.session.add(post)
        db.session.flush()
        db.session.refresh(post)
        db.session.commit()

        ## TODO make list of users to notify (now it notifies only author)
        notification = Notification(uid=root.created_by_id,pid=post.id)
        db.session.add(notification)
        db.session.commit()

        flash(f'Comment has been added.', 'success')
        return redirect(url_for('post', id=post.rid, _anchor=str(post.id)))

    elif form2.submit2.data and form2.validate_on_submit():
        ## check if logged in
        if current_user.is_authenticated is False:
            return redirect(url_for("login"))
        report = Report()
        report.reason = form2.reason.data
        report.reported_post = form2.reported_post.data
        report.created_by_id = current_user.id
        db.session.add(report)
        db.session.commit()
        flash(f'Post {report.reported_post} has been reported.', 'success')
        return redirect(url_for('post', id=root.id))

    return render_template('post.html', post=root, form1=form1, form2=form2, id=root.id)

@app.route("/user/<int:id>")
def user(id):
    page = db.paginate(db.select(Post).filter(
         Post.id==Post.rid,
         User.id==id
    ).order_by(Post.created_at.asc()), per_page=page_size)
    for post in page.items:
        post.display_content = truncate_text_by_word(post.content, 120)
    return render_template("posts.html", pagination=page, user=user)

@app.route("/post_create", methods=['GET', 'POST'])
@login_required
def post_create():
    form = CreatePostForm()
    if form.validate_on_submit():
        post = Post()
        form.populate_obj(post)
        post.created_by_id = current_user.id
        post.level = 0
        db.session.add(post)
        db.session.flush()
        db.session.refresh(post)
        post.rid = post.id
        post.pid = post.id
        db.session.commit()
        flash(f'Post has been added.', 'success')
        return redirect(url_for('post', id=post.rid))
    return render_template('post_create.html', form=form)

@app.route("/post_update/<int:id>", methods=['GET', 'POST'])
@login_required
def post_update(id):
    post = Post.query.get_or_404(int(id))
    ## post can be updated only by original creator
    if post.created_by_id != current_user.id:
        flash(f'not allowed', 'error')
        return redirect(request.referrer or url_for('default_route'))
    form = UpdatePostForm(request.form, obj=post)
    if form.validate_on_submit():
        form.populate_obj(post)
        db.session.add(post)
        db.session.commit()
        flash(f'Post has been updated.', 'success')
        return redirect(url_for('post', id=post.rid, _anchor=str(post.id)))
    return render_template('post_update.html', form=form)

@app.route("/post_delete/<int:id>", methods=['GET', 'POST'])
@login_required
def post_delete(id):
    post = Post.query.get_or_404(int(id))
    ## post can be deleted only by original creator
    if post.created_by_id != current_user.id:
        flash(f'not allowed', 'error')
        return redirect(request.referrer or url_for('default_route'))
    form = DeletePostForm(request.form, obj=post)
    if form.validate_on_submit():
        ##db.session.delete(post)
        post.deleted_by_id = current_user.id
        db.session.commit()
        flash(f'Post has been deleted.', 'success')
        return redirect(url_for('post', id=post.rid, _anchor=str(post.id)))
    return render_template('post_delete.html', form=form)

@app.route("/notifications")
def notifications():
    page = db.paginate(db.select(Notification).where(Notification.uid==current_user.id), per_page=50)
    return render_template("notifications.html", pagination=page)

@app.errorhandler(404) 
def not_found(e): 
    return render_template("404.html") 

if __name__=="__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)
