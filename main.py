from flask import Flask, request, redirect
from github import Github
import os

g = Github(os.getenv("GITHUB_TOKEN"))

app = Flask('app')

@app.route('/comment', methods=['GET', 'POST'])
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


app.run(os.environ.get('PORT'))
