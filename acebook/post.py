from acebook.db import get_db
from flask import g

class Post():

  @classmethod
  def create(cls, title, body, user_id, user_profile_picture):
    db = get_db()
    db.execute(
      'INSERT INTO post (title, body, author_id, user_profile_picture)'
      ' VALUES (?, ?, ?,?)',
      (title, body, user_id, user_profile_picture)
    )
    db.commit()

  @classmethod
  def all(cls):
    db = get_db()

    db.execute('DROP TABLE IF EXISTS num_likes')

    db.execute(
      'CREATE TABLE num_likes AS'
      ' SELECT post_id, count(post_id) AS cnt'
      ' FROM likes'
      ' group by post_id'
    )

    db.execute(
      'UPDATE post SET num_likes ='
      ' (SELECT cnt FROM num_likes'
      ' WHERE post_id = post.id)'
      ' where EXISTS (SELECT cnt'
      ' FROM num_likes WHERE post_id = post.id)'
    )

    posts = db.execute(
      'SELECT p.id, title, body, created, author_id, username, num_likes, user_profile_picture'
      ' FROM post p JOIN user u ON p.author_id = u.id'
      ' ORDER BY created DESC'
    ).fetchall()

    return [
      Post(
        post['title'],
        post['body'],
        post['id'],
        post['created'],
        post['author_id'],
        post['username'],
        post['num_likes'],
        post['user_profile_picture']
      ) for post in posts
    ]

  @classmethod
  def find_by_id(cls, id):
    post = get_db().execute(
      'SELECT p.id, title, body, created, author_id, username, num_likes'
      ' FROM post p JOIN user u ON p.author_id = u.id'
      ' WHERE p.id = ?',
      (id,)
    ).fetchone()

    return Post(
      post['title'],
      post['body'],
      post['id'],
      post['created'],
      post['author_id'],
      post['username'],
      post['num_likes']
    )

  def __init__(self, title, body, id, created, author_id, username, num_likes, user_profile_picture):
    self.title = title
    self.body = body
    self.id = id
    self.created = created
    self.author_id = author_id
    self.username = username
    self.num_likes = num_likes
    self.user_profile_picture = user_profile_picture

  def update(self, title, body, id):
    db = get_db()
    db.execute(
      'UPDATE post SET title = ?, body = ?'
      ' WHERE id = ?',
      (title, body, id)
    )
    db.commit()

  def delete(self):
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (self.id,))
    db.commit()

  def like_post(self):
    db = get_db()
    db.execute(
      'INSERT INTO likes (user_id, post_id)'
      ' VALUES (?, ?)',
       (str(g.user), self.id)
    )
    db.commit()


