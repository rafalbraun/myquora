#!/usr/bin/python3
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response
import sqlite3

app = Flask(__name__)
dbname = "posts.db"

QUERY_CREATE_POST_TABLE = '''
create table if not exists POSTS (
	post_id INTEGER PRIMARY KEY, 
	root_id INTEGER, 
	parent_id INTEGER, 
	content TEXT,
	FOREIGN KEY(root_id) REFERENCES POSTS(post_id),
	FOREIGN KEY(parent_id) REFERENCES POSTS(post_id)
);
'''
## insert into posts(content) values("hello");
## insert into posts(content, root_id, parent_id) values("goodbye", 1, 1);
## insert into posts(content, root_id, parent_id) values("asdadasd", 100, 100);

QUERY_SELECT_POST="select post_id, parent_id, root_id, content from posts where root_id = ?"
QUERY_CREATE_POST=""
QUERY_UPDATE_POST=""
QUERY_DELETE_POST=""
QUERY_SELECT_POSTS=""

class Post:
    def __init__(self, post_id, content):
        self.post_id = post_id
        self.content = content
        self.comments = []

    def add_comment(self, comment):
        self.comments.append(comment)

    def __repr__(self):
        return f"Post(id={self.post_id}, content='{self.content}', comments={self.comments})"

@app.route("/post/<int:root_id>", methods=["GET"])
def post(root_id):
	with sqlite3.connect(dbname) as conn:
		rows = conn.execute(QUERY_SELECT_POST, (root_id,)).fetchall()
		post = build_post_hierarchy(rows)[0]
		return render_template("index.html", post=post)
	return render_template("index.html")

def build_post_hierarchy(tuples):
    posts = {}

    # First pass: Create all Post objects and store them in a dictionary by post_id
    for post_id, root_id, parent_id, content in tuples:
        posts[post_id] = Post(post_id, content)

    root_posts = []

    # Second pass: Organize posts into the hierarchy
    for post_id, root_id, parent_id, content in tuples:
        if post_id == root_id == parent_id:
            # This is a root post
            root_posts.append(posts[post_id])
        else:
            # This is a child post, add it to the parent's comments
            posts[parent_id].add_comment(posts[post_id])

    return root_posts

if __name__=="__main__":
	app.run(host='0.0.0.0', port=8080)
