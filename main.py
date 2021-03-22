from flask import Flask, request, redirect, make_response, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from github import Github
import os

app = Flask(__name__)
limiter = Limiter(
	app,
	key_func=get_remote_address,
	default_limits=["2 per minute"],
)

g = Github(os.getenv("GITHUB_TOKEN"))

app = Flask('app')

@app.errorhandler(429)
def ratelimit_handler(e):
	return make_response("<code><h1>Error:</h1>You may only post once per hour. This is due to spam. I know you are very likely not a spam commenter or a robot, but it's neccesary to do this. If you would like to post again, either comment through GitHub or wait for an hour.<br>Thanks!<br><br>- Cole</code>",429)

@limiter.request_filter
def ip_whitelist():
	print(request.remote_addr)
	return request.remote_addr == os.getenv("my_ip") or  request.remote_addr == os.getenv("my_ip2") or  request.remote_addr == os.getenv("my_ip3")

@app.route('/comment', methods=['GET'])
@limiter.exempt
def no_comment():
	return "<code>you must come here from a post! head over to <a href='//colewilson.xyz'>colewilson.xyz</a> to view one.</code>"

@app.route('/comment', methods=['POST'])
@limiter.limit("2/hour")
def create_comment():
	ititle = request.form['url']
	body = request.form['body']
	repo = g.get_repo("cole-wilson/colewilson.xyz")
	issues = {}
	for issue in repo.get_issues(state="open"):
		issues[issue.title] = issue
	if ititle not in issues:
		issue = repo.create_issue(ititle, body=f"Comments for the [{ititle}](https://colewilson.xyz/{ititle}) post.", labels=["comment"])
	else:
		issue = issues[ititle]
	issue.create_comment(body)
	return redirect(f"https://colewilson.xyz/{ititle}#comments", code=302)

port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)
