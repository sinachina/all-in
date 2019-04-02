from flask_uploads import configure_uploads
from apps import app,db,pagedown,loginmanager,ck,creat_folder,STATIC_DIR
from flask import render_template, url_for, flash, request, redirect, session, jsonify, json
from flask_script import Manager
from flask_mail import Mail,Message
import time,random,os
from threading import Thread
from .model import Role, UserProfile, Article, IpList, Comment, Reply,Follow,Likes
import hashlib,re
from .forms import NameForm, Login, Register, Profile, photosSet,PostForm,CommentForm,ReplyForm
from flask_login import login_user,login_required,logout_user,current_user
from functools import wraps
import uuid
from PIL import Image
from qqwry import QQwry
from .qqwe import drow
from werkzeug.utils import secure_filename




mail = Mail(app)
manager = Manager(app)
verificationCode = random.randint(1000, 9999)

configure_uploads(app, photosSet)
# 修剪头像
def compression_img(data):
    size= (120,120)
    im = Image.open(data)
    im.thumbnail(size)
    return im
# 生成初始头像
def default_avatar(email):
    size = 180
    default = 'monsterid'
    r = 'g'
    m = hashlib.md5()
    m.update(email.encode('utf-8'))
    hash = m.hexdigest()
    a_url = 'https://www.gravatar.com/avatar/{hash}?s={size}&d={default}&r={r}'.format(hash=hash,size=size,default=default,r=r)
    return a_url

def friends_circle():
    follow = Role.query.filter_by(uuid=current_user.uuid).first()
    follower = follow.followers
    followed = follow.followed
    list1 = []
    list2 = []
    for i in follower:
        list1.append(i.follower.uuid)
    for j in followed:
        list2.append(j.followed.uuid)

    friend_list = set(list1).intersection(set(list2))

    return friend_list





@loginmanager.user_loader
def load_user(user_id):
    return Role.query.get(int(user_id))

def md5(data):
    md = hashlib.md5()
    md.update(data.encode('utf-8'))
    data = md.hexdigest()
    return data

def send_async_email(app,send):
    with app.app_context():
        mail.send(send)

@app.route('/',methods=['POST','GET'])
def index():

    page = request.args.get('page', 1, type=int)
    article = Article.query.paginate(page, per_page=10, error_out=False)
    news = Article.query.order_by(Article.id.desc()).limit(5).all()
    posts = article.items
    ip = str(request.remote_addr)
    agen = str(request.user_agent)
    list = IpList()
    list.ip = ip
    list.agent = agen
    db.session.add(list)
    db.session.commit()
    return render_template('index.html', posts=posts, news=news, article=article)

@app.route('/youcanyoudo',methods=['POST','GET'])
def dele():
    posts = Article.query.all()
    return render_template('delete.html',posts=posts)

@app.route('/youcanyoudo/<int:id>',methods=['POST','GET'])
def delete(id):
    role = Article.query.filter_by(id=id).first()
    db.session.delete(role)
    db.session.commit()
    return dele()


@app.route('/send', methods=['POST', 'GET'])
def send_msg():
    msg = verificationCode
    ip = request.remote_addr
    send = Message(ip, sender='1623332700@qq.com', recipients=['940615834@qq.com'])
    send.body = "ip地址是{},验证码是{}".format(ip, msg)
    thread = Thread(target=send_async_email, args=[app, send])
    thread.start()
    return '发送成功!'
@app.route('/issue',methods=['POST','GET'])
def issue():
    title = request.form.get('issuet')
    say = request.form.get('issue')
    send = Message('反馈', sender='1623332700@qq.com',recipients=['940615834@qq.com'])
    send.body = "标题是{},内容是{}".format(title,say)
    thread = Thread(target=send_async_email, args=[app, send])
    thread.start()
    return '发送成功!'


@app.route('/login', methods=['GET', 'POST'])
def user_login():
    form = Login()
    if form.validate_on_submit():
        user = Role.query.filter_by(username=form.username.data).first()
        if not user:

            return regist()
        else:
            pwd =md5(form.password.data)
            if not user.check(str(pwd)):
                flash('密码错误')
                return render_template('login.html', form=form)
            else:
                login_user(user, True)
                flash('登陆成功')
            return redirect(url_for('index'))
    return render_template('login.html', form=form)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('注销成功')
    return redirect(url_for('index'))

@app.route('/users',methods=['GET','POST'])
def users():

    return render_template('.html')


@app.route('/register', methods=['GET', 'POST'])
def regist():
    form = Register()
    if form.validate_on_submit():
        user = Role.query.filter_by(username=form.username.data).first()
        if user:
            flash('用户名已经存在',category='err')
            return render_template('register.html', form=form)
        else:
            users = Role()
            uu_id =str(uuid.uuid4()).replace('-', '')
            users.uuid = uu_id
            users.username = form.username.data
            users.pwd = md5(form.password.data)
            users.email = form.email.data
            users.avatar = default_avatar(form.email.data)
            db.session.add(users)
            db.session.commit()
            login_user(users, True)
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

@app.route('/list',methods=['POST','GET'])
def listSql():

    page = request.args.get('page', 1, type=int)
    listt = Role.query.all()
    pagination = IpList.query.order_by(IpList.time.desc()).paginate(page, per_page=15, error_out=False)
    ip = pagination.items
    for i in ip:
        ip_data = i.ip
        q = QQwry()
        filename = os.path.join(STATIC_DIR, 'qqwry.dat')
        q.load_file(filename, loadindex=False)
        adders = q.lookup(ip_data)
        query_ip = IpList.query.order_by(IpList.time.desc()).filter_by(ip=ip_data).first()
        query_ip.adders = str(adders)
        db.session.commit()

    return render_template('list.html',  ip=ip, pagination=pagination, listt=listt)


#查询role表，如果存在profile表就修改列，如果不存在就添加
@app.route('/profile', methods=['POST', 'GET'])
@login_required
def profile():
    form = Profile()
    if form.validate_on_submit():
        user = UserProfile()
        fn = time.strftime('%Y%m%d%H%M%S') + '_%d' % random.randint(0, 100) + '.png'
        avata =form.avatar.data
        new = compression_img(avata)
        creat_folder(os.path.join(app.config['UPLOADS_FOLDER'], current_user.uuid))
        pic_dir = os.path.join(app.config['UPLOADS_FOLDER'], current_user.uuid, fn)
        new.save(pic_dir)
        header = Role.query.filter_by(uuid=current_user.uuid).first()
        folder = photosSet.url(current_user.uuid)
        header.avatar = folder+'/'+fn
        if header.profile:
            proid = UserProfile.query.filter_by(user_id=current_user.uuid).first()
            proid.nickname = form.nickname.data
            proid.gender = form.gender.data
            proid.intro = form.intro.data
            proid.birthday = form.birthday.data
            db.session.commit()
        else:
            user.user_id = current_user.uuid
            user.nickname = form.nickname.data
            user.birthday = form.birthday.data
            user.gender = form.gender.data
            user.intro = form.intro.data
            db.session.add(user)
            db.session.commit()
        return 'success'
    return render_template('profile.html', form=form)


@app.route('/e', methods=['POST', 'GET'])
@login_required
def ckeditor():
    form = PostForm()
    if form.validate_on_submit():
        post = Article()
        pic_ = form.pic.data
        if pic_ is not None:
            fn = time.strftime('%Y%m%d%H%M%S') + '_%d' % random.randint(0, 100) + '.png'
            creat_folder(os.path.join(app.config['UPLOADS_FOLDER'], current_user.uuid))
            pic_dir = os.path.join(app.config['UPLOADS_FOLDER'], current_user.uuid, fn)
            pic = Image.open(pic_)
            pic.save(pic_dir)

            folder = 'uploads'+'/'+ current_user.uuid+'/'+fn
            post.img = folder 

        post.uuid = current_user.uuid
        post.tittle = form.title.data
        post.body = form.body.data
        print(form.body.data)
        print(pic_)
        obj = post.body
        obj = re.compile('</?\w+[^>]*>').sub('', obj)
        post.show = obj
        post.body_html = form.body.data
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('ck.html', form=form)

@app.route('/posts/<int:id>',methods=['POST','GET'])
def posts(id):
    form = CommentForm()
    replies = ReplyForm()
    post = Article.query.filter_by(id=id).first()
    user = post.role
    comments = post.comments
    post.view += 1
    db.session.commit()
    return render_template('posts.html', posts=post, user=user, form=form, comments=comments, replies=replies)
@app.route('/t')
def show():
    return render_template('test.html')

#非本人查看个人信息，
@app.route('/profile/<username>',methods=['POST','GET'])
def profileid (username):
    user = Role.query.filter_by(username=username).first()

    profiles = UserProfile.query.filter_by(user_id=user.uuid).first()

    return render_template('profiles.html', user=user, profile=profiles)



@app.route('/ckdemo',methods=['POST','GET'])
def ckdemo():
    form=PostForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        return showbody(title, body)
    return render_template('ckdemo.html', form=form)

@app.route('/showbody',methods=['POST','GET'])
def showbody(title, body):
    return render_template('show.html', title=title, body=body)

@app.route('/follow/<username>', methods=['POST','GET'])
@login_required
def follow(username):
    user = Role.query.filter_by(username=username).first()
    if user is None:
        flash('不存在用户')
        return redirect(url_for('index'))
    if current_user.is_following(user):
        flash('你已经关注该用户了')
        return redirect(url_for('profileid', username=username))
    current_user.follow(user)

    return redirect(url_for('profileid', username=username))

@app.route('/unfollow/<username>', methods=['POST','GET'])
@login_required
def unfollow(username):
    user = Role.query.filter_by(username=username).first()
    if user is None:
        flash('不存在用户')
        return redirect(url_for('index'))
    current_user.unfollow(user)
    flash('取关成功')
    return redirect(url_for('profileid', username=username))

@app.route('/followers/<username>', methods=['POST','GET'])
def followers(username):
    user = Role.query.filter_by(username=username).first()
    if user is None:
        flash('用户不存在')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=10, error_out=False
    )
    follows = pagination.items
    return render_template('followed.html', user=user, pagination=pagination,
                           follows=follows)

@app.route('/followed_by/<username>')
def followed_by(username):
    user = Role.query.filter_by(username=username).first()
    if user is None:
        flash('用户不存在')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(page, per_page=10, error_out=False)
    follows = pagination.items
    return render_template('followers.html', user=user, pagination=pagination, follows=follows)


@app.route('/posts/<int:id>/comment', methods=['POST', 'GET'])
@login_required
def comment(id):
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment()
        comment.article_id = id
        comment.user_id = current_user.uuid
        comment.body = form.body.data
        db.session.add(comment)
        db.session.commit()
    return redirect(url_for('posts', id=id))


@app.route('/posts/<int:id>/<int:comment>')
def delete_comment(id, comment):
    comments = Comment.query.filter_by(id=comment).first()
    db.session.delete(comments)
    db.session.commit()
    return redirect(url_for('posts', id=id))

@app.route('/posts/<int:id>/reply/<int:comment>',methods=['POST', 'GET'])
def reply_comment(id, comment):
    form = ReplyForm()
    if form.validate_on_submit():
        replies = Reply()
        replies.comment_id = comment
        replies.replies_id = current_user.uuid
        replies.body = form.body.data
        db.session.add(replies)
        db.session.commit()
    return redirect(url_for('posts', id=id))

@app.route('/friends', methods=['POST','GET'])
@login_required
def friends():
    page = request.args.get('page', 1, type=int)
    quer_y = current_user.friends_post
    article = quer_y.order_by(Article.addtime.desc()).paginate(
        page, per_page=15, error_out=False
    )
    posts = article.items

    return render_template('friends.html', posts=posts, article=article)

@app.route('/like/<int:id>',methods=['POST','GET'])
@login_required
def like(id):
    if current_user.is_liked(id):
        flash('您已经赞了这篇文章')
        return redirect(url_for('posts',id=id))
    current_user.like(id)
    return redirect(url_for('posts', id=id))

@app.route('/unlike/<int:id>',methods=['POST','GET'])
@login_required
def unlike(id):
    current_user.unlike(id)
    return redirect(url_for('posts', id=id))


@app.route('/vue' ,methods=['GET','POST'])
def vue_say():
    listt = Role.query.all()
    ip = IpList.query.order_by(IpList.time.desc()).all()
    t = {}
    for i in ip:
        t['ip'] = i.ip
        t['adress'] = i.adders
        print(t)
    return jsonify(t)

@app.route('/vue/list', methods=['GET','POST'])
def vue_list():
   # listt = Role.query.all()
    ip = IpList.query.order_by(IpList.time.desc()).all()
    t = []
    for i in ip:
        t.append(i.to_json())
    return jsonify(t)

@app.route('/mp/posts',methods=['POST','GET'])
def get_posts():
    posts_ = Article.query.all()
    return jsonify({
        'posts':[post.to_dict() for post in posts_]
    })

@app.route('/get_json_comment/<article_id>',methods=['POST','GET'])
def get_comment_json(article_id):
    comments = Comment.query.filter_by(article_id=article_id)
    return jsonify({
        'comment':[comment.to_json() for comment in comments]
    })

@app.route('/get_json_reply/<comment>',methods=['POST','GET'])
def get_json_reply(comment):
    reply = Reply.query.filter_by(comment_id=comment)
    print('reply get success!')
    r = []
    for i in reply:
        r.append(i.to_json())
    return jsonify(r)

@app.route('/request_data',methods=['POST','GET'])
def request_data():
    data = request.values.get('data')
    print(data)
    return redirect(url_for('get_json_reply',comment=data))

@app.route('/ttt',methods=['GET'])
def ttt():
    posts = Article.query.all()
    t=[]
    r = []
    for i in posts:
        for j in i.comments.all():
            t.append(j.to_json())

    print(t)

    return jsonify({
        'comment':t
    })
