from datetime import datetime, timedelta, timezone
import unittest
from app import app, db
from app.models import User, Post, Followers
from typing import List
from sqlalchemy import select

with app.app_context():
    username = 'xavi'
    user = db.session.execute(select(User).where(User.username==username)).scalar_one_or_none()
    xs = select(Post).where(User.username=='xavi')
    print(db.session.execute(xs).all())


'''
class UserModelCase(unittest.TestCase):

    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'  # restore original
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username='susan')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_avatar(self):
        u = User(username='john', email='john@example.com')
        self.assertEqual(u.avatar(128), (
            'https://www.gravatar.com/avatar/'
            'd4c74594d841139328695756648b6bd6'
            '?d=identicon&s=128'
        ))

    def test_follow(self):
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        self.assertEqual(list(u1.followed), [])
        self.assertEqual(list(u1.followers), [])

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(len(u1.followed), 1)
        self.assertEqual(u1.followed[0].username, 'susan')
        self.assertEqual(len(u2.followers), 1)
        self.assertEqual(u2.followers[0].username, 'john')

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(len(u1.followed), 0)
        self.assertEqual(len(u2.followers), 0)

    def test_follow_posts(self):
        # create four users
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        u3 = User(username='mary', email='mary@example.com')
        u4 = User(username='david', email='david@example.com')
        db.session.add_all([u1, u2, u3, u4])

        # create four posts
        now = datetime.now(timezone.utc)
        p1 = Post(body="post from john", user=u1,
                  timestamp=now + timedelta(seconds=1))
        p2 = Post(body="post from susan", user=u2,
                  timestamp=now + timedelta(seconds=4))
        p3 = Post(body="post from mary", user=u3,
                  timestamp=now + timedelta(seconds=3))
        p4 = Post(body="post from david", user=u4,
                  timestamp=now + timedelta(seconds=2))
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        # setup followers
        u1.follow(u2)  # john follows susan
        u1.follow(u4)  # john follows david
        u2.follow(u3)  # susan follows mary
        u3.follow(u4)  # mary follows david
        db.session.commit()

        # check followed posts of each user
        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()
        self.assertEqual(f1, [p2, p4, p1])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])


if __name__ == '__main__':
    unittest.main(verbosity=2)
'''