#!/usr/bin/python3
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response
import sqlite3
import json
from pprint import pprint

app = Flask(__name__)
dbname = "posts.db"

QUERY_CREATE_POST_TABLE = '''
create table if not exists POSTS (
	post_id INTEGER PRIMARY KEY, 
	root_id INTEGER, 
	parent_id INTEGER, 
	content TEXT,
	created_by INTEGER,
	created_at INTEGER,
	updated_by INTEGER,
	updated_at INTEGER,
	deleted_by INTEGER,
	deleted_at INTEGER,	
	FOREIGN KEY(root_id) REFERENCES POSTS(post_id),
	FOREIGN KEY(parent_id) REFERENCES POSTS(post_id)
);
'''

QUERY_SELECT_POST_WITH_COMMETS="select post_id, root_id, parent_id, content from posts where root_id = ?"
QUERY_SELECT_POST="select post_id, root_id, parent_id, content from posts where post_id = ?"
QUERY_CREATE_POST="insert into posts(content) values(?)"
QUERY_UPDATE_POST=""
QUERY_DELETE_POST=""
QUERY_AFTER_CREATE="update posts set parent_id=?, root_id=? where post_id=?"
QUERY_SELECT_POSTS="select post_id, content from posts where post_id=root_id"
QUERY_COMMENT_POST="insert into posts(root_id, parent_id, content) values(?,?,?)"

@app.route("/posts", methods=["GET"])
def posts():
	with sqlite3.connect(dbname) as conn:
		cursor = conn.cursor()
		rows = cursor.execute(QUERY_SELECT_POSTS).fetchall()
		posts = []
		for row in rows:
			posts.append(Post(row[0],row[1]))
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
		return render_template("post.html", post=result[0])

@app.route("/post/create", methods=["GET","POST"])
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
def post_comment(parent_id):
	content = request.form.get('content')
	with sqlite3.connect(dbname) as conn:
		cursor = conn.cursor()
		## get parent to obtain root_id and parent_id
		parent = cursor.execute(QUERY_SELECT_POST, (parent_id,)).fetchone()
		post_id, root_id, _, _ = parent
		comment = cursor.execute(QUERY_COMMENT_POST, (root_id, parent_id, content))
		return redirect(url_for(f'post', root_id=root_id))

@app.route("/post/update/<int:post_id>", methods=["GET","POST"])
def post_update():
	pass

@app.route("/post/delete/<int:post_id>", methods=["GET"])
def post_delete():
	pass

class Post:
	def __init__(self, post_id, content):
		self.post_id = post_id
		self.content = content
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

	for post_id, root_id, parent_id, content in tuples:
		posts[post_id] = Post(post_id, content)

	root_posts = []

	for post_id, root_id, parent_id, content in tuples:
		if post_id == root_id == parent_id:
			root_posts.append(posts[post_id])
		else:
			posts[parent_id].add_reply(posts[post_id])

	return root_posts

if __name__=="__main__":
	app.run(host='0.0.0.0', port=8080)
