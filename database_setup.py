
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, func, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base) :
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250),)
    


class BookmarkCategory(Base):
    __tablename__ = 'bookmark_category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(250), default=" Category Description")
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    resources = relationship("Resource", cascade="all, delete-orphan")

    @property
    def serialize(self):
        #Returns object data in easily serializable format (for implementing JSON end points)
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

class Resource(Base):
    __tablename__ = 'resource'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    url = Column(String(250))
    date_time = Column (DateTime(timezone=True), default=func.now()) # 
    notes = Column(String(500), default="Add your notes here")
    screenshot = Column(String(600), default="/static/images/default.png")
    category_id = Column(Integer, ForeignKey('bookmark_category.id'))
    bookmark_category = relationship(BookmarkCategory)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)


    @property
    def serialize(self):
        #Returns object data in easily serializable format (for implementing JSON end points)
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'date_time': str(self.date_time),
            'notes': self.notes,
            'category_id': self.category_id 
        }




engine = create_engine('postgres://ztmbqjryytprzu:KS8GVxNR6jWPQ4QxOrzwrD0BZq@ec2-54-197-238-19.compute-1.amazonaws.com:5432/d2jkttgdh3816k')


Base.metadata.create_all(engine)
