#!/usr/bin/python3
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response
import sqlite3

dbname = "posts.db"
QUERY_SELECT_POSTS="select post_id, parent_id, root_id, content from posts"

def getposts():
    rows = []
    with sqlite3.connect(dbname) as conn:
        cursor = conn.cursor()
        rows = cursor.execute(QUERY_SELECT_POSTS).fetchall()
    return rows

class Post:
    def __init__(self, post_id, content):
        self.post_id = post_id
        self.content = content
        self.comments = []

    def add_comment(self, comment):
        self.comments.append(comment)

    def __repr__(self):
        return f"Post(id={self.post_id}, content='{self.content}', comments={self.comments})"


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


# Example usage:
tuples = [
    (1, 1, 1, "Root Post 1"),  # root post
    (2, 1, 1, "Comment on Post 1 (same level as Root Post 1)"),  # sibling comment to the root post
    (3, 1, 2, "Comment on Post 2"),  # child comment of post 2
    (4, 4, 4, "Root Post 2"),  # another root post
    (5, 4, 4, "Comment on Post 4"),  # sibling comment to root post 2
    (6, 4, 5, "Comment on Post 5"),  # child comment of post 5
]

#tuples = getposts()
result = build_post_hierarchy(tuples)

for root in result:
    print(root)