from flask import session
from flask import abort
from functools import wraps


# 返回用户是否登录
def if_login():
    username = session.get('username')
    if username is not None:
        return True
    return False


# 返回用户名,如果未登录就返回None
def get_username():
    return session.get('username')


# 返回当前用户是否是博客主人
def is_owner():
    from config import con
    return session.get('username') == con.blog_owner


# 将一维列表按个数分成二维列表
def page_spliter(items, num):
    res = []

    while items:
        now = items[0:num]
        del (items[0:num])
        res.append(now)

    return res


# 装饰器:如果未登录就给404
def login_dec(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not if_login():
            abort(404)
        return func(*args, **kwargs)
    return wrapper


# 装饰器:如果不是博客主人就给404
def owner_dec(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not is_owner():
            abort(404)
        return func(*args, **kwargs)
    return wrapper


# 装饰器:如果登录了就给404
def unlogin_dec(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if if_login():
            abort(404)
        return func(*args, **kwargs)
    return wrapper


# 判断一个字符串数字是否为int,flask路由允许的<int:xxx>像01,-0123用这个函数验证都返回False
def is_int(content):
    if content.startswith('0') or content.startswith('-0') or '.' in content:
        return False
    try:
        int(content)
    except ValueError:
        return False
    return True
