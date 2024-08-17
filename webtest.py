from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    post = {
    "id": 0,
    "content": 'aaa',
    "replies": [
        {
            "id": 1,
            "content": "This is the first comment",
            "replies": [
                {
                    "id": 2,
                    "content": "This is a reply to the first comment",
                    "replies": []
                },
                {
                    "id": 3,
                    "content": "This is another reply to the first comment",
                    "replies": [
                        {
                            "id": 4,
                            "content": "This is a nested reply",
                            "replies": []
                        }
                    ]
                }
            ]
        },
        {
            "id": 5,
            "content": "This is a second top-level comment",
            "replies": []
        }
    ]
    }
    return render_template('comments.html', post=post)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
