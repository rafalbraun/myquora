import sqlite3

dbname = "posts.db"

QUERY_SELECT_USERNAME="select username, password from users where username = ?"

def validate_user_signup(username, password):
	errors = []
	if len(username) <= 5:
		errors.append("username too short")
	if len(username) > 30:
		errors.append("username too long")
	if len(password) <= 3:
		errors.append("password too short")
	if len(password) > 30:
		errors.append("password too long")
	with sqlite3.connect(dbname) as conn:
		cursor = conn.cursor()
		row = cursor.execute(QUERY_SELECT_USERNAME, (username,)).fetchone()
		if row is not None:
			errors.append("username already taken")
	return errors

## 1. check if content not too large
## 2. check if content not empty
## 3. check if user can post (?)
## 4. make always sure that we are not commenting on archived post
def validate_post_create(content):
	errors = []
	if len(content) == 0:
		errors.append("empty content")
	if len(content) > 2000:
		errors.append("content too large")
	return errors

## 1. check if content not too large
## 2. check if content not empty
## 3. check if user can update (is owner or admin) (?)
## 4. check if original post exists
def validate_post_update(content):
	errors = []
	if len(content) == 0:
		errors.append("empty content")
	if len(content) > 2000:
		errors.append("content too large")
	return errors

## 1. check if content not too large
## 2. check if content not empty
## 3. check if level not too deep (?)
## 4. check if parent exists - assume parent is correct
## 5. sanitize/escape content from dangerous chars (?)
## 6. check if user can post (?)
## 7. make always sure that we are not commenting on archived post
def validate_post_comment(content):
	errors = []
	if len(content) == 0:
		errors.append("empty content")
	if len(content) > 2000:
		errors.append("content too large")
	return errors

def validate_post_delete():
	pass
