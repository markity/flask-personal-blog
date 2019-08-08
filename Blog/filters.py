from config import con


# 同str的sliit
def split(content, basis):
    if basis in content:
        result = content.split(basis)
    else:
        result = [content]
    return result


# 同切片
def intercept(content, first, last):
    return content[first:last]


# 注册过滤器函数
def register_filters():
    env = con.app.jinja_env
    env.filters['split'] = split
    env.filters['intercept'] = intercept
