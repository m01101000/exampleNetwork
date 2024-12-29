from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

# Datenbank-Verbindung
DATABASE_URI = 'postgresql://postgres:super@localhost:5432/db1_postgreSQL'
engine = create_engine(DATABASE_URI)

# Basisklasse für Modelle
Base = declarative_base()

#####################################################################################

# Modelle erstellen
class User(Base):
    __tablename__ = 'user'

    UserID = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String(255), nullable=False)
    Email = Column(String(255), nullable=False, unique=True)
    CreatedAt = Column(DateTime, default=datetime.utcnow)

    posts = relationship("Post", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    likes = relationship("Like", back_populates="user")
    friendships = relationship("Friendship", foreign_keys='[Friendship.UserID1]', back_populates="user1")


class Post(Base):
    __tablename__ = 'post'

    PostID = Column(Integer, primary_key=True, autoincrement=True)
    UserID = Column(Integer, ForeignKey('user.UserID'), nullable=False)
    Content = Column(Text, nullable=True)
    CreatedAt = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")
    likes = relationship("Like", back_populates="post")


class Comment(Base):
    __tablename__ = 'comment'

    CommentID = Column(Integer, primary_key=True, autoincrement=True)
    PostID = Column(Integer, ForeignKey('post.PostID'), nullable=False)
    UserID = Column(Integer, ForeignKey('user.UserID'), nullable=False)
    Content = Column(Text, nullable=False)
    CreatedAt = Column(DateTime, default=datetime.utcnow)

    post = relationship("Post", back_populates="comments")
    user = relationship("User", back_populates="comments")


class Like(Base):
    __tablename__ = 'like'

    LikeID = Column(Integer, primary_key=True, autoincrement=True)
    PostID = Column(Integer, ForeignKey('post.PostID'), nullable=False)
    UserID = Column(Integer, ForeignKey('user.UserID'), nullable=False)
    CreatedAt = Column(DateTime, default=datetime.utcnow)

    post = relationship("Post", back_populates="likes")
    user = relationship("User", back_populates="likes")


class Friendship(Base):
    __tablename__ = 'friendship'
    __table_args__ = (UniqueConstraint('UserID1', 'UserID2', name='unique_friendship'),)

    FriendshipID = Column(Integer, primary_key=True, autoincrement=True)
    UserID1 = Column(Integer, ForeignKey('user.UserID'), nullable=False)
    UserID2 = Column(Integer, ForeignKey('user.UserID'), nullable=False)
    CreatedAt = Column(DateTime, default=datetime.utcnow)

    user1 = relationship("User", foreign_keys=[UserID1], back_populates="friendships")


# Tabellen erstellen
if __name__ == '__main__':
    # Erstellen aller Tabellen
    Base.metadata.create_all(engine)
    print("Tabellen wurden erfolgreich erstellt.")
