from app import app, db
from app.models import User, Post
from sqlalchemy import select

with app.app_context():
    session = db.session
    u = select(User.last_seen).where(User.username == 'Bamanye Ronald')
    print(session.execute(u).all())