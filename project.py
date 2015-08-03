from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, jsonify
from BeautifulSoup import BeautifulSoup
import urllib2

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, BookmarkCategory, Resource, User

from flask import session as login_session #works like a dictionary and we can  store values in it for the longevity of a user's session with the server
import random
import string
import db_helper

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests #similar to urlib2

CLIENT_ID = json.loads(open('client_secrets.json','r').read())['web']['client_id']

import cloudinary
import cloudinary.uploader
import cloudinary.api

cloudinary.config(
  cloud_name = "aui3",
  api_key = "227915768443584",
  api_secret = "FyXF-xhkTL9gouMr7hWW2ScmmWM"
)

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///bookmarks.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()




#login user
@app.route('/login')
def showLogin():
    #32 characters long and a mix of upper and lower case letters.
    # a (cross-site request forgery) forger will have to guess this key if we wants to make requests on the user's behalf.
    #check to make sure the user and login_session have the same state value when the user authenticates
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    print "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state, login_session=login_session)

#google connect
@app.route('/gconnect', methods=['POST'])
def gconnect():
    #check if the token that the client sends to the server request.args.get('state') is the same as the token that the server sent the client login_session['state']
    #ensures that the client is making the request and not a malicious script
   

    if request.args.get('state')!= login_session['state']:
        response= make_response(json.dumps('Invalid state parameter'),401)#??
        response.headers['Content-Type'] = 'application/json'
        return response

    code = request.data #collect the one time code that the client sends (via the ajax call). this is the code that google sends on authoirzation..

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')

        oauth_flow.redirect_uri = 'postmessage'

        credentials = oauth_flow.step2_exchange(code)

    except FlowExchangeError:
        print "here"
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        print response
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    print "in connect"
    print access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    print  "gplus_id"
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    print login_session;
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        print access_token
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if a user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
      #user does not exist, create user
      user_id =  createUser(login_session)
    login_session['user_id'] = user_id




    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"

    return output



# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token

    print "in discoinnect"
    print access_token

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
   

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("Successfully disconnected")
        return redirect(url_for('showCategories'))
    else:
        
        # For whatever reason, the given token was invalid.
        
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        
        return response

#Show all bookmark categories
@app.route('/')
@app.route('/bookmark_categories/')
def showCategories():
    category_list = session.query(BookmarkCategory)
    # list of recently added items
    recent_list = session.query(Resource).order_by(Resource.date_time.desc()).limit(5)
    
    if 'user_id' in login_session:
        print "user id %s", login_session['user_id']
        return render_template("bookmark_categories.html", recent_list=recent_list, category_list=category_list, user_id=login_session['user_id'], login_session=login_session)
    else:
        print "no user id"
        return render_template("bookmark_categories.html", recent_list=recent_list, category_list=category_list, user_id= "" )
            


# Add a new bookmarkcategory
@app.route('/bookmark_categories/new/', methods = ['GET', 'POST'])
def newCategory():
    # check if a user is logged before letting them proceed
    if 'username'  not in login_session:
        return redirect('/login')
    
    if request.method == 'POST':
        newCategory = BookmarkCategory (name= request.form['name'], description=request.form['description'], user_id=login_session['user_id'])
        session.add(newCategory)
        session.commit()
        flash("New Category Added")
        return redirect(url_for('showCategories'))
    else:
        return render_template("new_category.html", login_session=login_session)



#Edit a bookmark category
@app.route('/bookmark_categories/<int:category_id>/edit/', methods=['GET','POST'])
def editCategory(category_id):
    # check if a user is logged before letting them proceed
    if 'username'  not in login_session:
        return redirect('/login')

    editedCategory = session.query(BookmarkCategory).filter_by(id=category_id).one()

    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
        if request.form['description']:
            editedCategory.description = request.form['description']
        session.add(editedCategory)
        session.commit()
        flash("Category Edited")
        return redirect(url_for('showCategories'))

    else :
        return render_template("edit_category.html", category_id = category_id, category=editedCategory, login_session=login_session)


#delete a bookmark category
@app.route('/bookmark_categories/<int:category_id>/delete/', methods= ['GET', 'POST'])
def deleteCategory(category_id):
    # check if a user is logged before letting them proceed
    if 'username'  not in login_session:
        return redirect('/login')

    toBeDeletedCategory = session.query(BookmarkCategory).filter_by(id=category_id).one()

    if request.method == 'POST':
        delete_bookmarks_in_category(category_id)
        session.delete(toBeDeletedCategory)
        session.commit()
        flash("Category Deleted")
        return redirect(url_for('showCategories'))
    else :
        return render_template('delete_category.html', category=toBeDeletedCategory,login_session=login_session)



# Show all bookmarks in a category
@app.route('/bookmark_categories/<int:category_id>/')
@app.route('/bookmark_categories/<int:category_id>/resources/')
def showResources(category_id):
    resources_list = session.query(Resource).filter_by(category_id=category_id)
    category_list = session.query(BookmarkCategory)
    
    # check if a user is logged and send session information to the template if user present
    if 'user_id' in login_session:
        return render_template ("bookmark_resources.html", resources_list=resources_list, category_id=category_id, user_id=login_session['user_id'], login_session=login_session, category_list=category_list)
    else:
        return render_template ("bookmark_resources.html", resources_list=resources_list, category_id=category_id, user_id="",category_list=category_list)    


# Add a new bookmark resource
@app.route('/bookmark_categories/<int:category_id>/resources/new/', methods=['GET', 'POST'])
def newResource(category_id):
    
    #check if a user is logged in before letting them proceed
    if 'username'  not in login_session:
        
        return redirect('/login')
    name=''
    if request.method == 'POST':
        if request.form["url"]:
            #using the BeautifulSoup module to automatically extract the title of the URl to be added as a bookmark
            soup = BeautifulSoup(urllib2.urlopen(request.form["url"]))
            title = soup.find('title')
            #if the BeautifulSoup module can not extract a title, use the url as the name
            if not title:
                name= request.form["url"]
            else:
                name= soup.title.string
            #take a screen shot of the url using cloudinary    
            image= cloudinary.CloudinaryImage(request.form['url'], type = "url2png").build_url(crop = "fill", width = 150, height = 200, gravity = "north", sign_url = True)
            bookmark = Resource (url=request.form["url"], name=name, category_id=category_id, screenshot=image ,user_id= login_session['user_id'])
            session.add(bookmark)
            session.commit()
            flash("New Bookmark Resource Added")
        return redirect(url_for('showResources', category_id=category_id))
    else :
        return render_template('new_resource.html', category_id=category_id, login_session=login_session)


#Edit a bookmark resource
@app.route('/bookmark_categories/<int:category_id>/resources/<int:resource_id>/edit/', methods=['GET','POST'])
def editResource(category_id,resource_id):
    
    #check if a user is logged in before letting them proceed
    if 'username'  not in login_session:
        return redirect('/login')
    
    toBeEditedResource = session.query(Resource).filter_by(id=resource_id).one()
    
    if request.method == 'POST':

        if request.form ['name']:
            toBeEditedResource.name = request.form ['name']

        if request.form ['url']:
            toBeEditedResource.url = request.form[ 'url']

        if request.form ['notes']:
            toBeEditedResource.notes = request.form ['notes']

        session.add(toBeEditedResource)
        session.commit()
        flash("Bookmark Edited")

        return redirect(url_for('showResources',category_id=category_id))
    else :
        return render_template("edit_resource.html", category_id=category_id, resource_id=resource_id, resource=toBeEditedResource, login_session=login_session)


#Delete a bookmark resource.
@app.route('/bookmark_categories/<int:category_id>/resources/<int:resource_id>/delete/', methods=['GET','POST'])
def deleteResource(category_id,resource_id):
    
    #check if a user is logged in before letting them proceed
    if 'username'  not in login_session:
        return redirect('/login')

    toBeDeletedResource = session.query(Resource).filter_by(id=resource_id).one()

    if request.method== 'POST':
        session.delete(toBeDeletedResource)
        session.commit()
        flash("Bookmark deleted")
        return redirect(url_for('showResources',category_id=category_id))
    else :
        return render_template('delete_resource.html', category_id=category_id, resource_id=resource_id, resource=toBeDeletedResource, login_session=login_session)


#Edit  a bookmark note.
@app.route('/bookmark_categories/<int:category_id>/resources/<int:resource_id>/edit_notes/', methods=['GET', 'POST'])
def editNotes(category_id,resource_id):
    #check if a user is logged in before letting them proceed
    if 'username'  not in login_session:
        return redirect('/login')
    
    resource = session.query(Resource).filter_by(id=resource_id).one()
    
    if request.method == 'POST':
        resource.notes = request.form['notes']
        session.add(resource)
        session.commit()
        flash("Note Edited")
        return redirect(url_for('showResources',category_id=category_id))
    else:
        return render_template("edit_notes.html", category_id=category_id,resource_id=resource_id, resource=resource, login_session=login_session)

# Helper Functions

#create a new user
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

# get user data
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

# get user id
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# helper function to assist in cascade delete
def delete_bookmarks_in_category(category_id):
    print "here"
    bookmarks_list_del = session.query(Resource).filter_by(category_id=category_id)

    for b in bookmarks_list_del:
        session.delete(b)
        session.commit()


# JSON Endpoints


#JSON endpoint for all categories
@app.route('/bookmark_categories/JSON')
@app.route('/JSON')
def categoriesJSON():
    category_list = session.query(BookmarkCategory)
    return jsonify(Categories= [i.serialize for i in category_list])

#JSON endpoint for all bookmarks in a category
@app.route('/bookmark_categories/<int:category_id>/resources/JSON')
@app.route('/bookmark_categories/<int:category_id>/JSON')
def bookmarksInCategory(category_id):
    bookmarks_list = session.query(Resource).filter_by(category_id=category_id)
    return jsonify(BookmarKs=[i.serialize for i in bookmarks_list])

#JSON endpoint for one bookmarkresource
@app.route('/bookmark_categories/<int:category_id>/resources/<int:resource_id>/JSON')
def bookmarkJSON(category_id,resource_id):
    bookmark = session.query(Resource).filter_by(id=resource_id).one()
    return jsonify(Bookmark= bookmark.serialize)

if __name__ == '__main__':
    
    try:
        app.secret_key = 'super_secret_key'
        app.debug = True
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print "^c Entered   "

        