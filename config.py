from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_caching import Cache
from flask import render_template


class Config:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = '8848TJSJ213nosadxx%%'
        # database
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
        # 配置第三方登录
        self.app.config['GITHUB_CLIENT_ID'] = '10d2c4c84164b35xxxxx'
        self.app.config['GITHUB_CLIENT_SECRET'] = '1efa82ee1ee791eae00029cfc20f5eacf8exxxxx'

        self.csrf = CSRFProtect(self.app)
        self.cache = Cache(self.app, config={'CACHE_TYPE': 'simple'})
        self.blog_owner = 'lwaix'


# 设置错误页面,执行一下让app知道有这个就行了,包括视图也是这样的
def set_errors():
    @con.app.errorhandler(404)
    @con.cache.cached(60 * 60 * 2)
    def page_not_found(e):
        return render_template('error.html', message='页面未找到'), 404

    @con.app.errorhandler(400)
    @con.cache.cached(60 * 60 * 2)
    def csrf_token_error(e):
        return render_template('error.html', message='请求异常:400'), 400

    @con.app.errorhandler(405)
    @con.cache.cached(60 * 60 * 2)
    def method_not_allow(e):
        return render_template('error.html', message='请求异常:405'), 405

    @con.app.errorhandler(500)
    @con.cache.cached(60 * 60 * 2)
    def internal_server_error(e):
        return render_template('error.html', message='服务器异常:500'), 500


def init():
    # 设置错误页面
    set_errors()

    # 如果数据库未创建,就创建数据库
    from User.models import db as user_db
    from Blog.models import db as blog_db
    user_db.create_all()
    blog_db.create_all()

    # 注册蓝图
    from User.views import user_r
    from Blog.views import blog_r
    con.app.register_blueprint(user_r, url_prefix='/')
    con.app.register_blueprint(blog_r, url_prefix='/')

    # 注册过滤器
    from Blog.filters import register_filters
    register_filters()


con = Config()
