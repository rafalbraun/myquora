#!/usr/bin/python3
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response, make_response, jsonify
from functools import wraps
from pprint import pprint
import sqlite3
import json
import math
from sqlite3 import Error

from validations import *

app = Flask(__name__)
app.secret_key = 'your_secret_key'
dbname = "posts.db"
page_size = 10

QUERY_CREATE_NOTIFICATIONS_TABLE = '''
create table if not exists NOTIFICATIONS (
	post_id 	TEXT,
	username 	TEXT,
	PRIMARY KEY(post_id, username),
	FOREIGN KEY(post_id) 	REFERENCES POSTS(post_id),
	FOREIGN KEY(username) 	REFERENCES USERS(username)	
);
'''
QUERY_CREATE_SESSIONS_TABLE = '''
create table if not exists SESSIONS (
	session_id 	TEXT PRIMARY KEY
	username 	TEXT,
	created_at 	INTEGER
);
'''
QUERY_CREATE_USER_TABLE = '''
create table if not exists USERS (
	username 	TEXT PRIMARY KEY,
	password 	TEXT
);
'''
QUERY_CREATE_POST_TABLE = '''
create table if not exists POSTS (
	post_id 	INTEGER PRIMARY KEY, 
	root_id 	INTEGER,
	parent_id 	INTEGER,
	source_id 	INTEGER,
	username 	TEXT,
	content 	TEXT,
	created_by 	INTEGER,
	created_at 	INTEGER,
	updated_by 	INTEGER,
	updated_at 	INTEGER,
	deleted_by 	INTEGER,
	deleted_at 	INTEGER,
	FOREIGN KEY(root_id) 	REFERENCES POSTS(post_id),
	FOREIGN KEY(parent_id) 	REFERENCES POSTS(post_id),
	FOREIGN KEY(username) 	REFERENCES POSTS(username)
);
'''

## select user queries
QUERY_CREATE_USER="insert into users(username, password) values(?,?)"
QUERY_SELECT_USER="select username, password from users where username = ?"
QUERY_SELECT_USER_WITH_NOTIFICATIONS="select username, (select count(post_id) from notifications where username=u1.username) from users u1 where username = ?"

## update/insert post queries
QUERY_COMMENT_POST="insert into posts(root_id, parent_id, content, username, created_at) values(?,?,?,?,datetime())"
QUERY_ARCHIVE_POST="insert into posts(content, username, source_id) values(?,?,?)"
QUERY_CREATE_POST="insert into posts(content, username, created_at) values(?,?,datetime())"
QUERY_UPDATE_POST="update posts set content=? where post_id=?"
QUERY_DELETE_POST="update posts set deleted_at=?, deleted_by=? where post_id=?"
QUERY_AFTER_CREATE="update posts set parent_id=?, root_id=? where post_id=?"

QUERY_COUNT_USER_NOTIFICATIONS="select COUNT(*) FROM notifications where username=?"
QUERY_SELECT_USER_NOTIFICATIONS='''
select 
	p1.post_id,
	p1.root_id,
	p1.parent_id,
	"",
	p1.username,
	p1.created_at,
	0,
	p1.source_id 
from notifications n1
left join posts p1
on p1.post_id = n1.post_id
where n1.username=? limit ? offset ?
'''

## select post queries
QUERY_SELECT_POST_WITH_COMMENTS='''
select 
	t1.post_id, 
	t1.root_id, 
	t1.parent_id, 
	t1.content, 
	t1.username, 
	t1.created_at, 
	(select count(post_id)-1 from posts where root_id=t1.post_id) as comment_count, 
	source_id
from posts t1
where root_id = ? and source_id is null
'''

QUERY_SELECT_POST='''
select 
	post_id, 
	root_id, 
	parent_id, 
	content, 
	username, 
	created_at, 
	(select count(post_id)-1 from posts where root_id=p.post_id) as comment_count, 
	source_id
from posts p
where post_id = ? and source_id is null
'''

## for post versions paged view
QUERY_COUNT_POST_VERSIONS='''
select count(post_id) 
from posts 
where post_id = ? or source_id = ?
'''

QUERY_SELECT_POST_VERSIONS='''
select 
	post_id, 
	root_id, 
	parent_id, 
	content, 
	username, 
	created_at, 
	0, 
	source_id
from posts 
where post_id = ? or source_id = ?
order by created_at limit ? offset ?
'''

## for user posts paged view
QUERY_COUNT_USER_POSTS='''
select count(distinct root_id) 
from posts 
where username=? and source_id is null and post_id=root_id
'''

QUERY_SELECT_USER_POSTS='''
select 
	post_id,
	root_id,
	parent_id,
	content,
	username,
	created_at,
	(select count(post_id)-1 from posts where root_id=p1.post_id) as comment_count,
	source_id
from posts p1
where username=? and post_id=root_id and source_id is null
order by root_id limit ? offset ?
'''

## for posts paged view on front page
QUERY_SELECT_POSTS='''
select 
	post_id,
	root_id,
	parent_id,
	content,
	username,
	created_at,
	(select count(post_id)-1 from posts where root_id=p.post_id) as comment_count,
	source_id 
from posts p
where source_id is null and post_id=root_id
order by created_at asc limit ? offset ?
'''

QUERY_COUNT_POSTS="select count(root_id) from posts where root_id=post_id and source_id is null"

## for paged view of single post - first select given page of comments and union with main post
QUERY_SELECT_POST_COMMENTS='''
select * from(
	select 
		t1.post_id, 
		t1.root_id, 
		t1.parent_id, 
		t1.content, 
		t1.username, 
		t1.created_at, 
		(select count(post_id)-1 from posts where root_id=t1.post_id) as comment_count, 
		t1.source_id 
	from posts t1 
	where root_id=? and source_id is null and post_id <> root_id limit ? offset ?
)
union 
	select 
		t2.post_id,
		t2.root_id,
		t2.parent_id,
		t2.content,
		t2.username,
		t2.created_at,
		(select count(post_id)-1 from posts where root_id=t2.post_id) as comment_count, 
		t2.source_id 
	from posts t2 
	where root_id=? and source_id is null and post_id = root_id
'''

QUERY_COUNT_POST_COMMENTS="select count(root_id)-1 from posts where root_id=?"

## for user comments paged view
QUERY_SELECT_USER_COMMENTS='''
select 
	t1.post_id, t1.root_id, t1.parent_id, t1.content, t1.username, t1.created_at, 0, t1.source_id,
	t2.post_id, t2.root_id, t2.parent_id, t2.content, t2.username, t2.created_at, 0, t2.source_id
from 
	(select post_id, root_id, parent_id, content, username, created_at, source_id from posts where username=? and source_id is null and root_id <> post_id order by created_at limit ? offset ?) t1
left join
	(select post_id, root_id, parent_id, content, username, created_at, source_id from posts) t2
on t1.root_id = t2.post_id
'''

QUERY_COUNT_USER_COMMENTS="select count(post_id) from posts where username=? and source_id is null and root_id <> post_id"

def login_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		auth_cookie = request.cookies.get('auth')
		if not auth_cookie:
			return redirect(url_for('signin'))
		return f(*args, **kwargs)
	return decorated_function

def pagination(count, rows):
	posts = []
	for row in rows:
		posts.append(Post(*row))
	page_count = math.ceil(count/page_size)
	page_range = range(1, page_count+1)
	return posts, page_count, page_range

@app.route("/", methods=["GET"])
def index():
	return render_template("index.html", userinfo=get_userinfo(request))

@app.route("/post/<int:root_id>", methods=["GET"])
def post_smart_view(root_id):
	with sqlite3.connect(dbname) as conn:
		cursor = conn.cursor()
		rows = cursor.execute(QUERY_SELECT_POST_WITH_COMMENTS, (root_id,)).fetchall()
		if len(rows) == 0:
			return render_template("not_found.html", post_id=root_id)
		result = build_post_hierarchy(rows)
		if len(result) != 1:
			return render_template("consistency_error.html", post_id=root_id)			
		return render_template("post.html", post=result[0], comment_count=len(rows)-1, userinfo=get_userinfo(request))

@app.route("/posts", methods=["GET"])
def posts():
	pagenum = request.args.get('page', default=1, type=int)
	offset = (pagenum-1) * page_size
	try:
		with sqlite3.connect(dbname) as conn:
			cursor = conn.cursor()
			count = cursor.execute(QUERY_COUNT_POSTS).fetchone()[0]
			rows = cursor.execute(QUERY_SELECT_POSTS, (page_size,offset)).fetchall()
			posts, page_count, page_range = pagination(count, rows)
			return render_template("posts.html", posts=posts, page_count=page_count, pagenum=pagenum, page_range=page_range, userinfo=get_userinfo(request))
	except Error as e:
		# Handle database connection errors
		return render_template("errors.html", errors=[e])

@app.route("/post_paged/<int:root_id>", methods=["GET"])
def post_paged_view(root_id):
	with sqlite3.connect(dbname) as conn:
		cursor = conn.cursor()
		count = cursor.execute(QUERY_COUNT_POST_COMMENTS, (root_id,)).fetchone()[0]
		last_page = math.ceil(count/page_size)
		pagenum = request.args.get('page', default=last_page, type=int)
		offset = (pagenum-1) * page_size
		rows = cursor.execute(QUERY_SELECT_POST_COMMENTS, (root_id,page_size,offset,root_id)).fetchall()
		posts, page_count, page_range = pagination(count, rows)
		return render_template("post_paged.html", root_id=root_id, posts=posts, page_count=page_count, pagenum=pagenum, page_range=page_range, userinfo=get_userinfo(request))

@app.route("/post/versions/<int:post_id>", methods=["GET"])
def post_versions(post_id):
	pagenum = request.args.get('page', default=1, type=int)
	offset = (pagenum-1) * page_size
	with sqlite3.connect(dbname) as conn:
		cursor = conn.cursor()
		count = cursor.execute(QUERY_COUNT_POST_VERSIONS, (post_id,post_id)).fetchone()[0]
		rows = cursor.execute(QUERY_SELECT_POST_VERSIONS, (post_id,post_id,page_size,offset)).fetchall()
		posts, page_count, page_range = pagination(count, rows)
		return render_template("versions.html", post_id=post_id, posts=posts, page_count=page_count, pagenum=pagenum, page_range=page_range, userinfo=get_userinfo(request))

@app.route("/user/posts/<string:username>", methods=["GET"])
def user_posts(username):
	pagenum = request.args.get('page', default=1, type=int)
	offset = (pagenum-1) * page_size
	with sqlite3.connect(dbname) as conn:
		cursor = conn.cursor()
		count = cursor.execute(QUERY_COUNT_USER_POSTS, (username,)).fetchone()[0]
		rows = cursor.execute(QUERY_SELECT_USER_POSTS, (username,page_size,offset)).fetchall()
		posts, page_count, page_range = pagination(count, rows)
		return render_template("user_posts.html", username=username, posts=posts, page_count=page_count, pagenum=pagenum, page_range=page_range, userinfo=get_userinfo(request))

@app.route("/user/comments/<string:username>", methods=["GET"])
def user_comments(username):
	pagenum = request.args.get('page', default=1, type=int)
	offset = (pagenum-1) * page_size
	with sqlite3.connect(dbname) as conn:
		cursor = conn.cursor()
		count = cursor.execute(QUERY_COUNT_USER_COMMENTS, (username,)).fetchone()[0]
		rows = cursor.execute(QUERY_SELECT_USER_COMMENTS, (username,page_size,offset)).fetchall()
		posts = build_post_parents(rows)
		roots = [(post.post_id, post.root_id, post.parent_id, post.content, post.username, post.comment_count, post.source_id) for post in posts]
		_, page_count, page_range = pagination(count, roots)
		return render_template("user_comments.html", username=username, posts=posts, page_count=page_count, pagenum=pagenum, page_range=page_range, userinfo=get_userinfo(request))

@app.route("/post/create", methods=["GET","POST"])
@login_required
def post_create():
	if request.method == 'GET':
		return render_template("post_create.html", userinfo=get_userinfo(request))
	if request.method == 'POST':
		content = request.form.get('content')
		username = request.cookies.get('auth')

		errors = validate_post_create(content)
		if len(errors) != 0: return render_template("errors.html", errors=errors)

		with sqlite3.connect(dbname) as conn:
			cursor = conn.cursor()
			cursor.execute(QUERY_CREATE_POST, (content,username))
			lastrowid = cursor.lastrowid
			cursor.execute(QUERY_AFTER_CREATE, (lastrowid,lastrowid,lastrowid))
			return redirect(url_for(f'post_smart_view', root_id=lastrowid))

@app.route("/post/<int:parent_id>/comment", methods=["POST"])
@login_required
def post_comment(parent_id):
	view = request.form.get('view')
	content = request.form.get('content')
	username = request.cookies.get('auth')
	with sqlite3.connect(dbname) as conn:
		cursor = conn.cursor()
		## get parent to obtain root_id and parent_id
		row = cursor.execute(QUERY_SELECT_POST, (parent_id,)).fetchone()
		parent = Post(*row)

		errors = validate_post_comment(content)
		if len(errors) != 0: return render_template("errors.html", errors=errors, userinfo=get_userinfo(request))

		cursor.execute(QUERY_COMMENT_POST, (parent.root_id, parent.post_id, content, username))
		lastrowid = cursor.lastrowid
		
		return redirect(url_for(f'post_smart_view', root_id=parent.root_id, _anchor=lastrowid, userinfo=get_userinfo(request)))

@app.route("/post/update/<int:post_id>", methods=["GET","POST"])
@login_required
def post_update(post_id):
	if request.method == 'GET':
		with sqlite3.connect(dbname) as conn:
			cursor = conn.cursor()
			row = cursor.execute(QUERY_SELECT_POST, (post_id,)).fetchone()
			post = Post(*row) 
			return render_template("post_update.html", post=post, userinfo=get_userinfo(request))
	if request.method == 'POST':
		new_content = request.form.get('content')

		errors = validate_post_update(new_content)
		if len(errors) != 0: return render_template("errors.html", errors=errors, userinfo=get_userinfo(request))

		with sqlite3.connect(dbname) as conn:
			cursor = conn.cursor()
			row = cursor.execute(QUERY_SELECT_POST, (post_id,)).fetchone()
			post = Post(*row)
			cursor.execute(QUERY_ARCHIVE_POST, (post.content,post.username,post.post_id))
			cursor.execute(QUERY_UPDATE_POST, (new_content,post.post_id))
			lastrowid = cursor.lastrowid
			return redirect(url_for(f'post_smart_view', root_id=post.root_id, _anchor=lastrowid))

@app.route("/post/delete/<int:post_id>", methods=["GET"])
@login_required
def post_delete():
	pass

def get_userinfo(request):
	username = request.cookies.get('auth')
	if username is None:
		return None
	else:
		with sqlite3.connect(dbname) as conn:
			cursor = conn.cursor()
			row = cursor.execute(QUERY_SELECT_USER_WITH_NOTIFICATIONS, (username,)).fetchone()
			userinfo = UserInfo(*row)
			return userinfo

@app.route("/user/notifications/<string:username>", methods=["GET"])
@login_required
def user_nofitications(username):
	pagenum = request.args.get('page', default=1, type=int)
	offset = (pagenum-1) * page_size
	with sqlite3.connect(dbname) as conn:
		cursor = conn.cursor()
		count = cursor.execute(QUERY_COUNT_USER_NOTIFICATIONS, (username,)).fetchone()[0]
		rows = cursor.execute(QUERY_SELECT_USER_NOTIFICATIONS, (username,page_size,offset)).fetchall()
		posts, page_count, page_range = pagination(count, rows)
		return render_template("user_notifications.html", username=username, posts=posts, page_count=page_count, pagenum=pagenum, page_range=page_range, userinfo=get_userinfo(request))

@app.route("/signup", methods=["GET","POST"])
def signup():
	if request.method == 'GET':
		return render_template("signup.html")
	if request.method == 'POST':
		username = request.form.get('username')
		password = request.form.get('password')

		errors = validate_user_signup(username, password)
		if len(errors) != 0: return render_template("errors.html", errors=errors)

		with sqlite3.connect(dbname) as conn:
			cursor = conn.cursor()
			cursor.execute(QUERY_CREATE_USER, (username, password))		## TODO check if not exists
			return redirect(url_for('posts'))

@app.route("/signin", methods=["GET","POST"])
def signin():
	if request.method == 'GET':
		return render_template("signin.html")
	if request.method == 'POST':
		username = request.form.get('username')
		password = request.form.get('password')
		if len(password) < 3 or len(password) > 30 or len(username) < 3 or len(username) > 30:
			return "Wrong username or password", 401
		with sqlite3.connect(dbname) as conn:
			cursor = conn.cursor()
			row = cursor.execute(QUERY_SELECT_USER, (username,)).fetchone()
			if row is None:
				return 'No such user', 401
			else:
				if username == row[0] and password == row[1]:
					# Create a response and set a cookie if login is successful
					resp = make_response(redirect(url_for('posts')))
					resp.set_cookie('auth', username, max_age=3600, httponly=True)  # Cookie valid for 1 hour
					return resp
				else:
					return 'Invalid credentials', 401

@app.route('/signout')
@login_required
def signout():
	resp = make_response(redirect(url_for('signin')))
	resp.set_cookie('auth', '', expires=0)
	return resp

class UserInfo:
	def __init__(self, username, notifications_count):
		self.username = username
		self.notifications_count = notifications_count	

class Post:
	def __init__(self, post_id, root_id, parent_id, content, username, created_at, comment_count=0, source_id=0):
		self.created_at = created_at
		self.post_id = post_id
		self.root_id = root_id
		self.parent_id = parent_id
		self.source_id = source_id
		self.content = content
		self.username = username
		self.comment_count = comment_count
		self.replies = []

	def add_reply(self, comment):
		self.replies.append(comment)

	def __repr__(self):
		return f"Post(id={self.post_id}, content='{self.content}', replies={self.replies})"

	def to_json(self):
		return {
			'post_id': self.post_id,
			'content': self.content,
			'replies': self.replies
		}

def build_post_hierarchy(tuples):
	posts = {}

	for post_id, root_id, parent_id, content, username, created_at, comment_count, source_id in tuples:
		posts[post_id] = Post(post_id, root_id, parent_id, content, username, created_at, comment_count, source_id)

	root_posts = []

	for post_id, root_id, parent_id, content, username, created_at, comment_count, source_id in tuples:
		if post_id == root_id == parent_id:
			root_posts.append(posts[post_id])
		else:
			posts[parent_id].add_reply(posts[post_id])

	return root_posts

def build_post_parents(tuples):
	posts = []

	for post_id, root_id, parent_id, content, username, created_at, comment_count, source_id, parent_post_id, parent_root_id, parent_parent_id, parent_content, parent_username, parent_created_at, parent_comment_count, parent_source_id in tuples:
		parent = Post(parent_post_id, parent_root_id, parent_parent_id, parent_content, parent_username, parent_created_at, parent_comment_count, parent_source_id)
		reply = Post(post_id, root_id, parent_id, content, username, created_at, comment_count, source_id)
		parent.add_reply(reply)
		posts.append(parent)

	return posts

if __name__=="__main__":
	app.run(debug=True, host='0.0.0.0', port=8080)
