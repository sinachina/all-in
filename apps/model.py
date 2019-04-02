from datetime import datetime
from flask import jsonify
from flask import url_for

from apps import db
import bleach
from flask_login import UserMixin
from markdown import markdown

class Follow(db.Model):
    __tablename__ = 'follows1'
    follower_id = db.Column(db.String(32), db.ForeignKey('role1.uuid'), primary_key=True)
    followed_id = db.Column(db.String(32), db.ForeignKey('role1.uuid'), primary_key=True)
    times = db.Column(db.DATETIME, default=datetime.now)

class Role(UserMixin,db.Model):
    __tablename__ = 'role1'
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(32), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    pwd = db.Column(db.String(80),  nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    avatar = db.Column(db.String(240), default='img/ad.jpg')
    addtime = db.Column(db.DATETIME, index=True, default=datetime.now)
    article = db.relationship('Article', backref='role')
    profile = db.relationship('UserProfile', backref='role')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    replies = db.relationship('Reply', backref='author', lazy='dynamic')
    likes = db.relationship('Likes', backref='author', lazy='dynamic')
    followed = db.relationship('Follow', foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'), lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id],
                               backref=db.backref('followed', lazy='joined'), lazy='dynamic',
                               cascade='all, delete-orphan')

    def check(self, pwd):#对比输入的密码与原密码
        return self.pwd == pwd

    def is_liked(self,post_id):
        return self.likes.filter_by(article_id=post_id).first() is not None

    def like(self,post_id):
        if not self.is_liked(post_id):
            l = Likes()
            l.article_id = post_id
            l.user_id = self.uuid
            db.session.add(l)
            db.session.commit()

    def unlike(self,post_id):
        l = self.likes.filter_by(article_id=post_id).first()
        if l:
            db.session.delete(l)
            db.session.commit()
    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            print(f)
            db.session.add(f)
            db.session.commit()

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.uuid).first()
        if f:
            db.session.delete(f)
            db.session.commit()

    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.uuid).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.uuid).first() is not None

    @property
    def friends_post(self):
        follow = Role.query.filter_by(uuid=self.uuid).first()
        follower = follow.followers
        followed = follow.followed
        list1 = []
        list2 = []
        for i in follower:
            list1.append(i.follower.uuid)
        for j in followed:
            list2.append(j.followed.uuid)
        friend_list = [x for x in list1 if x in list2]
        u = Article.query.filter(Article.uuid.in_(friend_list))
        return u

class Article(db.Model):
    __tablename__= 'article1'
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(32), db.ForeignKey('role1.uuid'),nullable=False)
    tittle = db.Column(db.String(128), nullable=False)
    collections = db.Column(db.Integer, default=0)
    view = db.Column(db.Integer, default=1)
    img = db.Column(db.String(240), default='img/blog/blog-3.jpg')
    show = db.Column(db.Text)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    addtime = db.Column(db.DATETIME, index=True, default=datetime.now)
    likes = db.relationship('Likes', backref='article', lazy='dynamic')
    comments = db.relationship('Comment', backref='article', lazy='dynamic')

#关系型数据表转Json时怎么转，在转化韩式中使用函数
    def to_dict(self):
        data  = {
            'id' :self.id,
            'uuid':self.uuid,
            'tittle':self.tittle,
            'view_count':self.view,
            'show':self.show,
            'body':self.body,
            'body_html':self.body_html,
            'time':self.addtime,
            'like_count':self.likes.count(),
            'comment':self.comments.count(),
            'link_':{
                'avatar' :self.role.avatar,
                'username':self.role.username
            },
            'comments':url_for('get_comment_json',article_id=self.id),
            'new_comment':{'comments':self.filter_c}
            # 这里是一个路由，怎样让他返回一个查询结果，而不仅仅是一个路由.添加函数，使其返回。在
        }
        return data

    @property
    def filter_c(self):
        comments=Comment.query.filter_by(article_id=self.id).all()
        return [comment.to_json() for comment in comments]

    '''
    json 返回一个comment，里面的
    comments 无法调用函数，不对，comments为什么只能生成一个路由，却无法返回函数。
    难道需要使用蓝本？还是我哪里出问题了
    '''

    @staticmethod
    def on_change_body(target,value,oldvalue,initator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img', 'video', 'div', 'iframe', 'p',
                        'br', 'span', 'hr', 'src', 'class']
        allowed_attrs = {'*':['class','pre'],
                         'a':['href','rel'],
                         'img':['src','alt']
        }
        target.body_html =bleach.linkify(bleach.clean(
            markdown(value,output_format=('html'),
                     tags =allowed_tags, strip=True, attributes=allowed_attrs)
        ))

db.event.listen(Article.body,'set',Article.on_change_body)

class Likes(db.Model):
    __tablename__ = 'likes1'
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article1.id'))
    user_id = db.Column(db.String(32), db.ForeignKey('role1.uuid'))
    time = db.Column(db.DATETIME, default=datetime.now)

    def to_json(self):
        dict = self.__dict__
        if 'sa_instance_state' in dict:
            del dict['sa_instance_state']
        return dict


class UserProfile(db.Model):
    __tablename__= 'userprofile1'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(32), db.ForeignKey('role1.uuid'))
    nickname = db.Column(db.String(80))
    gender = db.Column(db.String(80))
    birthday = db.Column(db.Date)
    intro = db.Column(db.Text)


class IpList(db.Model):
    __tablename__ = 'ip1'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(50))
    agent = db.Column(db.Text)
    adders = db.Column(db.String(300))
    time = db.Column(db.DATETIME, index=True, default=datetime.now)

    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict


class Comment(db.Model):
    __tablename__ = 'comments1'
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article1.id'))
    user_id = db.Column(db.String(32), db.ForeignKey('role1.uuid'))
    body = db.Column(db.String(200))
    time = db.Column(db.DATETIME, index=True, default=datetime.now)
    reply = db.relationship('Reply', backref='comments', lazy='dynamic')

    def to_json(self):
        data = {
            'id':self.id,
            'article_id':self.article_id,
            'user_id':self.user_id,
            'body':self.body,
            'time':self.time,
            'reply':url_for('get_json_reply',comment=self.id),
            '_link':{
                'avatar':self.author.avatar,
                'username':self.author.username
            },
            'replies':{
                'r':self.filter_reply
            }
        }
        return data
    #这里必须返回值是一个list,否则后续json话时无法成功
    @property
    def filter_reply(self):
        reply = Reply.query.filter_by(comment_id=self.id).all()
        return [r.to_json() for r in reply]




class Reply(db.Model):
    __tablename__ = 'replies1'
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments1.id'))
    replies_id = db.Column(db.String(32), db.ForeignKey('role1.uuid'))
    body = db.Column(db.String(100))
    time = db.Column(db.DATETIME, index=True, default=datetime.now)

    def to_json(self):
        data = {
            'id':self.id,
            'comment_id':self.comment_id,
            'replies_id':self.replies_id,

            'body':self.body,
            'time':self.time,
            '_link':{
                'avatar':self.author.avatar,
                'username':self.author.username
            }

        }

        return data



if __name__ =='__main__':
    db.drop_all()
    db.create_all()
