from app import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Text, func
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from hashlib import md5

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id:Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    username:Mapped[str] = mapped_column(String(64), index = True, unique = True)
    email:Mapped[str] = mapped_column(String(128), index = True, unique=True)
    password_hash:Mapped[str|None] = mapped_column(String(128))
    about_me:Mapped[Optional[str]] = mapped_column(String(200))
    last_seen:Mapped[datetime] = mapped_column(default=datetime.utcnow, server_default=func.now())

    post:Mapped[List['Post']] = relationship(back_populates='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?identicon&s={size}'

    def __repr__(self):
        return f'User({self.id.hex}, "{self.username}")'
    
class Post(db.Model):
    __tablename__ = 'posts'
    id:Mapped[int] = mapped_column(primary_key=True)
    user_id:Mapped[UUID] = mapped_column(ForeignKey('users.id'), index=True)
    body:Mapped[str] = mapped_column(Text)
    timestamp:Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)

    user:Mapped['User'] = relationship(back_populates='post')

    def __repr__(self):
        return f'Post({self.id}, "{self.user_id.hex}")'
    
@login.user_loader
def load_user(id):
    return db.session.get(User, UUID(id))

