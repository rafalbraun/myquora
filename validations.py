

def validate_signup():
	pass

def validate_signin():
	pass

def validate_post_create():
	pass

def validate_post_update():
	pass

def validate_post_delete():
	pass

## 1. check if content not too large
## 2. check if content not empty
## 3. check if level not too deep (?)
## 4. check if parent exists - assume parent is correct
## 5. sanitize/escape content from dangerous chars (?)
def validate_post_comment(content):
	errors = []
	if len(content) == 0:
		errors.append("empty content")
	if len(content) > 2000:
		errors.append("content too large")
	return errors

