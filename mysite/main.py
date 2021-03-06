# Import Module
import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, session, redirect, jsonify
from flask_sslify import SSLify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import json
import datetime
import math

with open('/home/TechnoPustakBlog/mysite/config.json', 'r') as c:
    params = json.load(c)["params"]


app = Flask(__name__)
sslify = SSLify(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///posts.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.secret_key = "super-secret-key"
app.config['UPLOAD_FOLDER'] = params['upload_location']
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD=  params['gmail-password']
)

mail = Mail(app)

class Comments(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    comment = db.Column(db.String(500), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    post = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)

class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    img_file = db.Column(db.String(12), nullable=False)
    date = db.Column(db.String(12), nullable=False)
    subhead = db.Column(db.String(12), nullable=False)
    ytlink = db.Column(db.String(1000), nullable=True)

    def __repr__(self) -> str:
        return f'{self.sno}-{self.title}'

@app.route('/lol')
def lol():
    return render_template('lol.html')

@app.route('/')
def home():
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts)/int(params['no_of_posts']))
    # [0:params['no_of_posts']]
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page=int(page)
    posts = posts[(page-1)*int(params['no_of_posts']):(page-1) * int(params['no_of_posts']) + int(params['no_of_posts'])]
    if (page==1):
        prev = '#'
        next = '/?page=' + str(page+1)
    elif (page==last) or (page==1):
        prev = '/?page=' + str(page-1)
        next = '#'
    else:
        prev = '/?page=' + str(page-1)
        next = '/?page=' + str(page+1)

    return render_template('index.html', params = params, posts = posts, prev = prev, next = next)

@app.route('/about')
def about():
    return render_template('about.html', params = params)

@app.route('/api/comment/<string:post>')
def commentapi(post):
    comments = Comments.query.filter_by(post=post).all()
    api = {}
    for comment in comments:
        api[comment.sno] = [comment.name, comment.email, comment.date, comment.comment]
    return jsonify(api)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if ('user' in session and session['user'] == params['admin_user']):
        posts = Posts.query.filter_by().all()
        return render_template('dashboard.html', params = params, posts = posts)

    if request.method == 'POST':
        username = request.form.get('uname')
        userpass = request.form.get('password')
        if (username == params['admin_user'] and userpass == params['admin_password']):
            session['user'] = username
            posts = Posts.query.filter_by().all()
            return render_template('dashboard.html', params = params, posts = posts)

    return render_template('login.html', params = params)

@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    if (request.method == 'POST'):
        f = request.files['file1']
        if 'mp3' in str(f):
            f.save(os.path.join('/home/TechnoPustakBlog/mysite/static/assets/audio/', secure_filename(f.filename)))
        else:
            f.save(os.path.join(params['upload_location'], secure_filename(f.filename)))
        return 'Uploaded successfully.'

@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/dashboard')

@app.route('/delete/<string:sno>', methods=["GET", "POST"])
def delete(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        post = Posts.query.filter_by(sno=sno).first()
        comment = Comments.query.filter_by(post=sno).all()
        for com in comment:
            db.session.delete(com)
        db.session.delete(post)
        db.session.commit()
        return redirect('/dashboard')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if (request.method == 'POST'):
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        mail.send_message('Techno Pustak site message from ' + name,
                          sender=email,
                          recipients = [params['gmail-user']],
                          body = f'Message - {message}\nPhone number - {phone}\nEmail - {email}'
                          )

    return render_template('contact.html', params = params)

@app.route('/edit/<string:sno>', methods=["GET", "POST"])
def edit(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        if request.method == "POST":
            title = request.form.get('title')
            subhead = request.form.get('subhead')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            ytlink = request.form.get('ytlink')
            date = datetime.datetime.now()

            if sno=='0':
                post = Posts(title = title, slug = slug, subhead = subhead, content = content, img_file = img_file, date = date, ytlink=ytlink)
                post_slug = Posts.query.filter_by(slug=slug).first()
                if post_slug:
                    return 'Slug is used.'
                else:
                    db.session.add(post)
                    db.session.commit()

            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.title = title
                post.slug = slug
                post.subhead = subhead
                post.content = content
                post.img_file = img_file
                post.ytlink = ytlink
                db.session.commit()

        post = Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html', params=params, sno = sno, post = post)

@app.route('/post/<string:post_slug>', methods=["GET", "POST"])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    if request.method == 'POST':
        name = request.form.get('name')
        post_comment = request.form.get('comment')
        email = request.form.get('email')
        date = datetime.datetime.now()
        post_no = post.sno
        entry = Comments(name = name, comment = post_comment, date = date, post = post_no, email = email)
        db.session.add(entry)
        db.session.commit()
        return redirect('/post/'+post.slug)

    comments = Comments.query.filter_by(post=post.sno).all()
    return render_template('post.html', params=params, post=post, comments = comments)

if __name__ == '__main__':
    app.run(threaded=True)