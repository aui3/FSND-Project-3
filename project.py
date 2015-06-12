from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, jsonify
from BeautifulSoup import BeautifulSoup
import urllib2

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, BookmarkCategory, Resource, User

from flask import session as login_session
import random
import string
import db_helper

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

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

##########
# Helper function
##############
def delete_bookmarks_in_category(category_id):
	print "here"
	bookmarks_list_del = session.query(Resource).filter_by(category_id=category_id)
	
	for b in bookmarks_list_del:
		session.delete(b)
		session.commit()

#Show all bookmark categories
@app.route('/')
@app.route('/bookmark_categories/')
def showCategories():
	category_list = session.query(BookmarkCategory)
	return render_template("bookmark_categories.html", category_list=category_list)


# Add a new bookmarkcategory
@app.route('/bookmark_categories/new/', methods = ['GET', 'POST'])
def newCategory():
	if request.method == 'POST':
		newCategory = BookmarkCategory (name= request.form['name'], description=request.form['description']) 
		session.add(newCategory)
		session.commit()
		flash("New Category Added")
		return redirect(url_for('showCategories'))
	else :
		return render_template("new_category.html")
	


#Edit a bookmark category
@app.route('/bookmark_categories/<int:category_id>/edit/', methods=['GET','POST'])
def editCategory(category_id):
	
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
		return render_template("edit_category.html", category_id = category_id, category=editedCategory)	


#delete a bookmark category
@app.route('/bookmark_categories/<int:category_id>/delete/', methods= ['GET', 'POST'])
def deleteCategory(category_id):
	
	toBeDeletedCategory = session.query(BookmarkCategory).filter_by(id=category_id).one()
	
	if request.method == 'POST':
		delete_bookmarks_in_category(category_id)
		session.delete(toBeDeletedCategory)
		session.commit()
		flash("Category Deleted")
		return redirect(url_for('showCategories'))
	else :
		return render_template('delete_category.html', category=toBeDeletedCategory)
		


# Show all bookmarks in a category
@app.route('/bookmark_categories/<int:category_id>/')
@app.route('/bookmark_categories/<int:category_id>/resources/')
def showResources(category_id):
	resources_list = session.query(Resource).filter_by(category_id=category_id)
	return render_template ("bookmark_resources.html", resources_list=resources_list, category_id=category_id)


# Add a new bookmark resource
@app.route('/bookmark_categories/<int:category_id>/resources/new/', methods=['GET', 'POST'])
def newResource(category_id):
	name=''
	if request.method == 'POST':
		if request.form["url"]:
			soup = BeautifulSoup(urllib2.urlopen(request.form["url"]))
			title = soup.find('title')
			#if the soup module can not extract a title, use the url as the name
			if not title:
				name= request.form["url"]
			else:
				name= soup.title.string
			image= cloudinary.CloudinaryImage(request.form['url'], type = "url2png").build_url(crop = "fill", width = 150, height = 200, gravity = "north", sign_url = True)
			bookmark = Resource (url=request.form["url"], name=name, category_id=category_id, screenshot=image)
			session.add(bookmark)
			session.commit()
			flash("New Bookmark Resource Added")
		return redirect(url_for('showResources', category_id=category_id))
	else :
		return render_template('new_resource.html', category_id=category_id)


#Edit a bookmark resource
@app.route('/bookmark_categories/<int:category_id>/resources/<int:resource_id>/edit/', methods=['GET','POST'])
def editResource(category_id,resource_id):
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
		return render_template("edit_resource.html", category_id=category_id, resource_id=resource_id, resource=toBeEditedResource)


#Delete a bookmark resource.
@app.route('/bookmark_categories/<int:category_id>/resources/<int:resource_id>/delete/', methods=['GET','POST'])
def deleteResource(category_id,resource_id):
	
	toBeDeletedResource = session.query(Resource).filter_by(id=resource_id).one()

	if request.method== 'POST':
		session.delete(toBeDeletedResource)
		session.commit()
		flash("Bookmark deleted")
		return redirect(url_for('showResources',category_id=category_id))
	else :
		return render_template('delete_resource.html', category_id=category_id, resource_id=resource_id, resource=toBeDeletedResource)
	

#Edit  a bookmark note.
@app.route('/bookmark_categories/<int:category_id>/resources/<int:resource_id>/edit_notes/', methods=['GET', 'POST'])
def editNotes(category_id,resource_id):
	resource = session.query(Resource).filter_by(id=resource_id).one()
	if request.method == 'POST':
		resource.notes = request.form['notes']
		session.add(resource)
		session.commit()
		flash("Note Edited")
		return redirect(url_for('showResources',category_id=category_id))
	else:
		return render_template("edit_notes.html", category_id=category_id,resource_id=resource_id, resource=resource)


##################
# JSON ENDPOINTS
##################

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
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host='0.0.0.0', port=5000)