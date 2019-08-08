from config import con
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy(con.app)


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(32), nullable=False, unique=False)
    content = db.Column(db.Text, nullable=False, unique=False)
    add_datetime = db.Column(db.DateTime, nullable=False, unique=False)
    edit_datetime = db.Column(db.DateTime, nullable=False, unique=False)
    # 发布者名称,未来可以拓展多用户的博客系统
    sender = db.Column(db.String(32), nullable=False, unique=False)
    # 阅读量
    read = db.Column(db.Integer, nullable=False, unique=False)

    # 新建保存博客并返回错误列表
    def add_with_save(self):
        title = self.title
        content = self.content
        sender = self.sender
        errors = []
        if not all((title, content, sender)):
            errors.append('参数不完整')
        # 没错误才保存
        if not errors:
            now = datetime.now()
            self.add_datetime = now
            self.edit_datetime = now
            self.read = 0
            db.session.add(self)
            db.session.commit()
        return errors

    # 得到当前博客的留言个数
    def get_com_len(self):
        return len(Comment.query.filter_by(blog_id=self.id).all())

    # 增加一个阅读量并保存
    def add_read(self):
        self.read += 1
        db.session.commit()

    # 编辑保存,并返回错误列表
    def edit_with_save(self, title, content):
        errors = []
        if not all((title, content)):
            errors.append('参数不完整')
        # 无错误才保存
        if not errors:
            self.edit_datetime = datetime.now()
            self.title = title
            self.content = content
            db.session.commit()
        return errors

    # 删除博客
    def delete_with_save(self):
        # 删除这个博客的所有留言
        Comment.query.filter_by(blog_id=self.id).delete()
        db.session.delete(self)
        db.session.commit()

    # 得到发布者对象
    def get_sender(self):
        from User.models import User
        return User.query.filter_by(username=self.sender).first()


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(32), nullable=False, unique=False)
    content = db.Column(db.Text, nullable=False, unique=False)
    add_datetime = db.Column(db.String(32), nullable=False, unique=False)
    # 对应博客id
    blog_id = db.Column(db.Integer, nullable=False, unique=False)

    # 新建保存留言,并返回错误列表
    def add_with_save(self):
        sender = self.sender
        content = self.content
        blog_id = self.blog_id
        errors = []
        if not all((sender, content, blog_id)):
            errors.append('参数不完整')
        if not 2 <= len(content) <= 300:
            errors.append('留言长度要在2-300之间')
        # 没错误才保存
        if not errors:
            content = content.strip()
            # 只允许两个换行共存,太多空行影响美观
            while '\r\n\r\n\r\n' in content:
                content = content.replace('\r\n\r\n\r\n', '\r\n\r\n')
            self.content = content
            self.add_datetime = datetime.now()
            db.session.add(self)
            db.session.commit()
        return errors

    # 得到发布者对象
    def get_sender(self):
        from User.models import User
        return User.query.filter_by(username=self.sender).first()
