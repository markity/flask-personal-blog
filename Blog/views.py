from flask import Blueprint
from flask import request
from flask import redirect
from flask import render_template
from flask import url_for
from tools import if_login
from tools import get_username
from tools import is_owner
from tools import page_spliter
from tools import login_dec
from tools import owner_dec
from tools import is_int
from .forms import BlogForm
from .forms import CommentForm
from .forms import SearchForm
from .models import Blog
from .models import Comment
from User.models import User
from mistune import markdown
from config import con
from flask import abort

blog_r = Blueprint('blog', __name__)


@blog_r.route('/', methods=['GET'])
@con.cache.cached(60*60*2)
def index():
    if request.method == 'GET':
        return redirect(url_for('blog.blogs_page', page_num=1))


@blog_r.route('/page/<page_num>/', methods=['GET'])
def blogs_page(page_num):
    if not is_int(page_num):
        abort(404)
    page_num = int(page_num)
    if request.method == 'GET':
        all_blogs = Blog.query.order_by(-Blog.id).all()
        split = page_spliter(all_blogs, 5)
        min_page = 1
        max_page = len(split)
        if max_page == 0:
            max_page = 1
            split = [[]]
        if page_num < min_page or page_num > max_page:
            abort(404)
        blogs = split[page_num-1]
        return render_template('Blog/blogs.html', if_login=if_login(), blogs=blogs, username=get_username(),
                               is_owner=is_owner(), this_page=page_num, min_page=min_page,
                               max_page=max_page)


@blog_r.route('/search/', methods=['POST'])
def search():
    if request.method == 'POST':
        form = SearchForm(formdata=request.form)
        content = form.search.data
        if content.strip():
            return redirect(url_for('blog.blogs_search', content=content, page_num=1))
        else:
            return render_template('Blog/errorList.html', errors=['请输入正确的搜索关键词'])


@blog_r.route('/search/<content>/<page_num>/', methods=['GET'])
def blogs_search(content, page_num):
    if not is_int(page_num):
        abort(404)
    page_num = int(page_num)
    if request.method == 'GET':
        all_blogs = Blog.query.order_by(-Blog.id).all()
        blogs = []
        content = content.strip()
        words = content.split(' ')
        for rb in all_blogs:
            for word in words:
                word_low = word.lower()
                if word_low in rb.title.lower() or word_low in rb.content.lower():
                    blogs.append(rb)
                    break
        split = page_spliter(blogs, 5)
        min_page = 1
        max_page = len(split)
        if max_page == 0:
            max_page = 1
            split=[[]]
        if page_num < min_page or page_num > max_page:
            abort(404)
        blogs = split[page_num - 1]
        return render_template('Blog/searchBlogs.html', blogs=blogs, this_page=page_num,
                               min_page=min_page, if_login=if_login(), max_page=max_page,
                               search=content)


@blog_r.route('/blog/add/', methods=['GET'])
@owner_dec
def get_add_blog():
    if request.method == 'GET':
        return render_template('Blog/addBlog.html')


@blog_r.route('/blog/add/', methods=['POST'])
@owner_dec
def post_add_blog():
    if request.method == 'POST':
        form = BlogForm(formdata=request.form)
        blog = Blog(title=form.title.data, content=form.content.data, sender=get_username())
        errors = blog.add_with_save()
        if not errors:
            return redirect(url_for('blog.get_blog', blog_id=blog.id))
        else:
            return render_template('Blog/errorList.html', errors=errors)


@blog_r.route('/blog/<blog_id>/edit/', methods=['GET'])
@owner_dec
def get_edit_blog(blog_id):
    if not is_int(blog_id):
        abort(404)
    blog_id = int(blog_id)
    if request.method == 'GET':
        blog = Blog.query.filter_by(id=blog_id).first_or_404()
        return render_template('Blog/editBlog.html', blog=blog)


@blog_r.route('/blog/<blog_id>/edit/', methods=['POST'])
@owner_dec
def post_edit_blog(blog_id):
    if not is_int(blog_id):
        abort(404)
    blog_id = int(blog_id)
    if request.method == 'POST':
        form = BlogForm(formdata=request.form)
        blog = Blog.query.filter_by(id=blog_id).first_or_404()
        errors = blog.edit_with_save(form.title.data, form.content.data)
        if not errors:
            return redirect(url_for('blog.get_blog', blog_id=blog_id))
        else:
            return render_template('Blog/errorList.html', errors=errors)


@blog_r.route('/blog/<blog_id>/delete/', methods=['GET'])
@owner_dec
def delete_blog(blog_id):
    if not is_int(blog_id):
        abort(404)
    blog_id = int(blog_id)
    if request.method == 'GET':
        blog = Blog.query.filter_by(id=blog_id).first_or_404()
        blog.delete_with_save()
        return redirect(url_for('blog.index'))


@blog_r.route('/blog/<blog_id>/', methods=['GET'])
def get_blog(blog_id):
    if not is_int(blog_id):
        abort(404)
    blog_id = int(blog_id)
    if request.method == 'GET':
        blog = Blog.query.filter_by(id=blog_id).first_or_404()
        m_content = markdown(blog.content)
        if '<p>' in m_content:
            m_content = m_content.replace('<p>', '')
        if '</p>' in m_content:
            m_content = m_content.replace('</p>', '')
        comments = Comment.query.filter_by(blog_id=blog_id).order_by(-Comment.id).all()
        blog.add_read()
        return render_template('Blog/blog.html', blog=blog, if_login=if_login(),
                               m_content=m_content, comments=comments)


@blog_r.route('/blog/<blog_id>/', methods=['POST'])
@login_dec
def post_comment(blog_id):
    if not is_int(blog_id):
        abort(404)
    blog_id = int(blog_id)
    if request.method == 'POST':
        form = CommentForm(formdata=request.form)
        user = User.query.filter_by(username=get_username()).first()
        comment = Comment(sender=user.username, content=form.content.data, blog_id=blog_id)
        errors = comment.add_with_save()
        if not errors:
            return redirect(url_for('blog.get_blog', blog_id=blog_id))
        else:
            return render_template('Blog/errorList.html', errors=errors)


@blog_r.route('/about/', methods=['GET'])
def about():
    if request.method == 'GET':
        return render_template('Blog/about.html', if_login=if_login())


@blog_r.route('/donate/', methods=['GET'])
def donate():
    return render_template('Blog/donate.html', if_login=if_login())
