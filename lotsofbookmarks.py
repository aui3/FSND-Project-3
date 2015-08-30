from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import BookmarkCategory, Base, Resource, User

engine = create_engine('postgres://ztmbqjryytprzu:KS8GVxNR6jWPQ4QxOrzwrD0BZq@ec2-54-197-238-19.compute-1.amazonaws.com:5432/d2jkttgdh3816k')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="Robo Barista", email="ayesha.nizami@gmail.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()


#Category 1 HTML resources

category1 = BookmarkCategory(user_id=1, name="HTML", description="HTML resources")

session.add(category1)
session.commit()


resource1 = Resource( name="W3School HTML Tutorial", url="http://www.w3schools.com/html/", notes="These are my notes W3School HTML Tutorial", bookmark_category=category1, user_id=1)

session.add(resource1)
session.commit()


resource2 = Resource( name="Beginner HTML Tutorial by htmldog", url="http://htmldog.com/guides/html/beginner/", notes="Beginner HTML Tutorial by htmldog" , bookmark_category=category1, user_id=1)

session.add(resource2)
session.commit()


resource3 = Resource( name="Beginner HTML Tutorial codecademy", url="http://www.codecademy.com/en/tracks/web", notes="These are my notes Beginner HTML Tutorial codecademy" , bookmark_category=category1, user_id=1)

session.add(resource3)
session.commit()

resource4 = Resource( name="Special Characters in HTML", url="https://www.utexas.edu/learn/html/spchar.html", notes="These are my notes Special Characters in HTML" , bookmark_category=category1, user_id=1)

session.add(resource4)
session.commit()



#Category 2 CSS resources

category2 = BookmarkCategory(user_id=1, name="CSS", description="CSS resources")

session.add(category2)
session.commit()


resource1 = Resource( name="W3School CSS Tutorial", url="http://www.w3schools.com/css/", notes="These are my notes W3School CSS Tutorial", bookmark_category=category2, user_id=1)

session.add(resource1)
session.commit()


resource2 = Resource( name="The beauty of CSS Design", url="http://www.csszengarden.com/", notes="These are my notes The beauty of CSS Design" , bookmark_category=category2, user_id=1)

session.add(resource2)
session.commit()


resource3 = Resource( name="A Complete Guide to Flexbox",  url="https://css-tricks.com/snippets/css/a-guide-to-flexbox/", notes="These are my notes A Complete Guide to Flexbox" , bookmark_category=category2, user_id=1)

session.add(resource3)
session.commit()

resource4 = Resource( name="CSS Media Queries", url="https://developer.mozilla.org/en-US/docs/Web/Guide/CSS/Media_queries", notes="These are my notes CSS media queries" , bookmark_category=category2, user_id=1)

session.add(resource4)
session.commit()



#Category 3 JavaScript resources

category3 = BookmarkCategory(user_id=1, name="JavaScript", description="Javascript resources")

session.add(category3)
session.commit()


resource1 = Resource( name="W3School Javascript Tutorial", url="http://www.w3schools.com/js/", notes="These are my notes W3School CSS Tutorial", bookmark_category=category3, user_id=1)

session.add(resource1)
session.commit()


resource2 = Resource( name="Eloquent JavaScript", url="http://eloquentjavascript.net/", notes="These are my notes The beauty of CSS Design" , bookmark_category=category3, user_id=1)

session.add(resource2)
session.commit()


resource3 = Resource( name="Google Javascript Style Guide",  url="https://google-styleguide.googlecode.com/svn/trunk/javascriptguide.xml", notes="These are my notes Google Javascript Style Guide" , bookmark_category=category3, user_id=1)

session.add(resource3)
session.commit()

resource4 = Resource( name="Javascript Objects in Detail", url="http://javascriptissexy.com/javascript-objects-in-detail/", notes="These are my notes CSS media queries" , bookmark_category=category3, user_id=1)

session.add(resource4)
session.commit()




print "added menu items!"
