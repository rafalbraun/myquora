#!/usr/bin/python3
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response
import sqlite3

dbname = "posts.db"
QUERY_SELECT_POST="select post_id, parent_id, root_id, content from posts where root_id = ?"

class Post:
    def __init__(self, post_id, content):
        self.post_id = post_id
        self.content = content
        self.comments = []

    def add_comment(self, comment):
        self.comments.append(comment)

    def __repr__(self):
        return f"Post(id={self.post_id}, content='{self.content}', comments={self.comments})"

def post(root_id):
	with sqlite3.connect(dbname) as conn:
		cursor = conn.cursor()
		rows = cursor.execute(QUERY_SELECT_POST, (root_id,)).fetchall()
		post = build_post_hierarchy(rows)
		return post

'''
assuming we have list of tuples like [(post_id, root_id, parent_it, content),...] w get the top post where post_id == root_it == parent_id and then we put hierarchically all other posts so that always post with post_id being child_id is put in comments of its parent
'''
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

p = post(1)
print(p[0])


