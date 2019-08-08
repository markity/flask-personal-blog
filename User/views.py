from flask import Blueprint
from flask import render_template
from flask import request
from flask import session
from flask import redirect
from flask import url_for
from flask import abort
from flask_github import GitHub
from flask_github import GitHubError
from User.models import User
from config import con
from tools import if_login
from tools import login_dec
from tools import unlogin_dec

user_r = Blueprint('user', __name__, template_folder='templates/User')
github = GitHub(con.app)

error = None


@user_r.route('/login/', methods=['GET'])
@unlogin_dec
def login():
    if request.method == 'GET':
        global error
        if error is None:
            return render_template('User/login.html')
        else:
            e = error
            error = None
            return render_template('User/login.html', error=e)


@user_r.route('/login/github/', methods=['GET'])
@unlogin_dec
def login_with_github():
    if request.method == 'GET':
        return github.authorize(scope='repo')


@user_r.route('/login/github/callback/', methods=['GET'])
@unlogin_dec
@github.authorized_handler
def authorized(oauth_token):
    if request.method == 'GET':
        global error
        # 只要为None就说明不存在或者伪造
        if oauth_token is None:
            error = '获得Github授权失败!!'
            return redirect(url_for('user.login'))
        try:
            r = github.get('user', access_token=oauth_token)
        except GitHubError:
            error = '获得Github授权失败!!'
            return redirect(url_for('user.login'))
        username = r.get('login')
        user = User.query.filter_by(username=username).first()
        if user is None:
            user = User(user_id=r.get('id'), username=username, email=r.get('email'))
            user.add_with_save()
        session['username'] = username
        return redirect(url_for('blog.index'))


@user_r.route('/logout/', methods=['GET'])
@login_dec
def logout():
    if request.method == 'GET':
        del session['username']
        return redirect(url_for('blog.index'))
