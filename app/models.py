from app import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Text, func, Table, Column, select, and_,union
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from hashlib import md5

Followers = db.Table(
    'followers',
    db.metadata,
    Column('follower_id', ForeignKey('users.id'), primary_key=True, nullable=False),
    Column('followed_id', ForeignKey('users.id'), primary_key=True, nullable=False),
)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id:Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    username:Mapped[str] = mapped_column(String(64), index = True, unique = True)
    email:Mapped[str] = mapped_column(String(128), index = True, unique=True)
    password_hash:Mapped[str|None] = mapped_column(String(128))
    about_me:Mapped[Optional[str]] = mapped_column(String(200))
    last_seen:Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc), server_default=func.now())

    post:Mapped[List['Post']] = relationship(back_populates='author')
    followed:Mapped[List['User']] = relationship(
        'User',
        secondary=Followers,
        primaryjoin=(Followers.c.follower_id == id),
        secondaryjoin=(Followers.c.followed_id == id),
        back_populates='followers',
        lazy = 'select'
    )
    followers:Mapped[List['User']] = relationship(
        'User',
        secondary=Followers,
        primaryjoin=(Followers.c.followed_id == id),
        secondaryjoin=(Followers.c.follower_id == id),
        back_populates='followed',
        lazy = 'select'   
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def __repr__(self):
        return f'User({self.id.hex}, "{self.username}")'
    
    def is_following(self, user):
        return db.session.scalar(
            select(Followers).where(
                and_(
                    Followers.c.follower_id == self.id,
                    Followers.c.followed_id == user.id
                )
            )
        ) is not None
    
    def follow(self,user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def followed_posts(self):
        posts_followed = (select(Post)
                      .join(Followers, Followers.c.followed_id == Post.user_id)
                      .where(Followers.c.follower_id == self.id)
                      )
        own = select(Post).where(Post.user_id == self.id)
        union_query = posts_followed.union_all(own).subquery()
        return select(Post).join(union_query, Post.id == union_query.c.id).order_by(Post.timestamp.desc())
                                 
class Post(db.Model):
    __tablename__ = 'posts'
    id:Mapped[int] = mapped_column(primary_key=True)
    user_id:Mapped[UUID] = mapped_column(ForeignKey('users.id'), index=True)
    body:Mapped[str] = mapped_column(Text)
    timestamp:Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), index=True)

    author:Mapped['User'] = relationship(back_populates='post')

    def __repr__(self):
        return f'Post({self.id}, "{self.body}")'

    def __eq__(self, other):
        if isinstance(other, Post):
            return self.id == other.id
        return False
    
@login.user_loader
def load_user(id):
    return db.session.get(User, UUID(id))
