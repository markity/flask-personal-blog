from flask_wtf import FlaskForm
from wtforms import StringField

# 目前表单只用来接收提交的内容,验证在模型里(wtf的轮子用不懂,自己验证更加方便)


class BlogForm(FlaskForm):
    title = StringField()
    content = StringField()


class CommentForm(FlaskForm):
    content = StringField()


class SearchForm(FlaskForm):
    search = StringField()
