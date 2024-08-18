#!/usr/bin/python3
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response, make_response, jsonify
import sqlite3
import json
from pprint import pprint
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for securely signing the session cookie
dbname = "posts.db"

# Hardcoded credentials for simplicity
USERNAME = 'admin'
PASSWORD = 'password'

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

QUERY_SELECT_POST_WITH_COMMETS="select post_id, root_id, parent_id, content, username from posts where root_id = ?"
QUERY_CREATE_USER="insert into users(username, password) values(?,?)"
QUERY_SELECT_USER="select username, password from users where username = ?"
QUERY_SELECT_POST="select post_id, root_id, parent_id, content from posts where post_id = ?"
QUERY_CREATE_POST="insert into posts(content) values(?)"
QUERY_UPDATE_POST="update posts set content=? where post_id=?"
QUERY_DELETE_POST="update posts set deleted_at=?, deleted_by=? where post_id=?"
QUERY_AFTER_CREATE="update posts set parent_id=?, root_id=? where post_id=?"
##QUERY_SELECT_POSTS="select t1.root_id, t1.comment_count, t2.content, t2.username from (select root_id, count(post_id) as comment_count from posts group by root_id) t1 left join (select root_id, content, username from posts) t2 on t1.root_id = t2.root_id"
QUERY_SELECT_POSTS="select post_id, content, 0, username from posts where post_id=root_id"
QUERY_COMMENT_POST="insert into posts(root_id, parent_id, content) values(?,?,?)"

def login_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		auth_cookie = request.cookies.get('auth')
		if not auth_cookie or auth_cookie != USERNAME:
			return redirect(url_for('signin'))
		return f(*args, **kwargs)
	return decorated_function

@app.route("/index", methods=["GET"])
def index():
	return render_template("index.html")

@app.route("/posts", methods=["GET"])
def posts():
	with sqlite3.connect(dbname) as conn:
		cursor = conn.cursor()
		rows = cursor.execute(QUERY_SELECT_POSTS).fetchall()
		posts = []
		for row in rows:
			posts.append(Post(row[0],row[1],row[2],row[3]))
		return render_template("index.html", posts=posts)

@app.route("/post/<int:root_id>", methods=["GET"])
def post(root_id):
	with sqlite3.connect(dbname) as conn:
		cursor = conn.cursor()
		rows = cursor.execute(QUERY_SELECT_POST_WITH_COMMETS, (root_id,)).fetchall()
		if len(rows) == 0:
			return render_template("not_found.html", post_id=root_id)
		result = build_post_hierarchy(rows)
		if len(result) != 1:
			return render_template("consistency_error.html", post_id=root_id)			
		return render_template("post.html", post=result[0], comment_count=len(rows))

@app.route("/post/create", methods=["GET","POST"])
@login_required
def post_create():
	if request.method == 'GET':
		return render_template("post_create.html")
	if request.method == 'POST':
		content = request.form.get('content')
		## TODO validate content
		with sqlite3.connect(dbname) as conn:
			cursor = conn.cursor()
			cursor.execute(QUERY_CREATE_POST, (content,))
			lastrowid = cursor.lastrowid
			cursor.execute(QUERY_AFTER_CREATE, (lastrowid,lastrowid,lastrowid))
			return redirect(url_for(f'post', root_id=lastrowid))

@app.route("/post/<int:parent_id>/comment", methods=["POST"])
@login_required
def post_comment(parent_id):
	content = request.form.get('content')

	if len(content) == 0:
		error = "empty content"
		return render_template("error.html", error=error)
	if len(content) > 2000:
		error = "content too large"
		return render_template("error.html", error=error)

	with sqlite3.connect(dbname) as conn:
		cursor = conn.cursor()
		## get parent to obtain root_id and parent_id
		parent = cursor.execute(QUERY_SELECT_POST, (parent_id,)).fetchone()
		post_id, root_id, _, _ = parent
		comment = cursor.execute(QUERY_COMMENT_POST, (root_id, parent_id, content))
		return redirect(url_for(f'post', root_id=root_id))

@app.route("/post/update/<int:post_id>", methods=["GET","POST"])
@login_required
def post_update(post_id):
	if request.method == 'GET':
		with sqlite3.connect(dbname) as conn:
			cursor = conn.cursor()
			row = cursor.execute(QUERY_SELECT_POST, (post_id,)).fetchone()
			post = Post(row[0], row[3]) 
			return render_template("post_update.html", post=post)
	if request.method == 'POST':
		content = request.form.get('content')
		with sqlite3.connect(dbname) as conn:
			cursor = conn.cursor()
			cursor.execute(QUERY_UPDATE_POST, (content,post_id))
			parent = cursor.execute(QUERY_SELECT_POST, (post_id,)).fetchone()
			_, root_id, _, _ = parent
			return redirect(url_for(f'post', root_id=root_id))

@app.route("/post/delete/<int:post_id>", methods=["GET"])
def post_delete():
	pass

@app.route("/signup", methods=["GET","POST"])
def signup():
	if request.method == 'GET':
		return render_template("signup.html")
	if request.method == 'POST':
		username = request.form.get('username')
		password = request.form.get('password')
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
		with sqlite3.connect(dbname) as conn:
			cursor = conn.cursor()
			row = cursor.execute(QUERY_SELECT_USER, (username,)).fetchone()
			if row is None:
				return 'no such user', 401
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

class Post:
	def __init__(self, post_id, content, username, comment_count=0):
		self.post_id = post_id
		self.content = content
		self.replies = []
		self.username = username
		self.comment_count = comment_count

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

	for post_id, root_id, parent_id, content, username in tuples:
		posts[post_id] = Post(post_id, content, username)

	root_posts = []

	for post_id, root_id, parent_id, content, username in tuples:
		if post_id == root_id == parent_id:
			root_posts.append(posts[post_id])
		else:
			posts[parent_id].add_reply(posts[post_id])

	return root_posts

if __name__=="__main__":
	app.run(debug=True, host='0.0.0.0', port=8080)
