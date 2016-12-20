from flask import Flask, redirect, request, render_template
from redis import Redis
import os, random

app = Flask(__name__)
redis = Redis(host='redis')

port = os.getenv('PORT', 5000)
hostname = os.getenv('VIRTUAL_HOST', 'localhost:{}'.format(port))


def get_redirection(key):
    return redis.get(key)

def generate_random_string(length = 6) -> str:

    alpha_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"

    return ''.join([random.choice(alpha_chars) for x in range(length)])

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if not request.method == 'POST':
        return render_template('submission_form.html')

    submission_url = request.form['URL']
    submission_key = request.form['redirect-value']

    if not submission_url:
        return render_template('error.html', error_message="Please provide a URL.")

    if submission_key:
        if redis.get(submission_key):
            return render_template('error.html', error_message='The requested key has already been used, please try another.')
    else:
        submission_key = generate_random_string()

    try:
        redis.set(submission_key, submission_url)
    except Exception as ex:
        return render_template('error.html', error_message=str(ex))

    display_url = r'{}/r/{}'.format(hostname, submission_key)
    html_url = r'http://{}/r/{}'.format(hostname, submission_key)
    return render_template('submitted.html', html_url=html_url, display_url=display_url)

@app.route('/r/<key>', methods=['GET'])
def make_redirection(key):
    url = get_redirection(key)

    if not url:
        return render_template('error.html', error_message="Sorry, the requested URL was not found on the server.")

    url = str(url, encoding='utf8')

    if not url.lower().startswith('http://') or url.lower().startswith('https://'):
        url = 'http://' + url

    return redirect(url, code = 302)


if __name__ == '__main__':
    app.run()
