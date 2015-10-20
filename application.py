# imports
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item # , User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

#CLIENT_ID = json.loads(
#    open('client_secrets.json', 'r').read())['web']['client_id']
#APPLICATION_NAME = "Restaurant Menu Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Show all category & last item added
@app.route('/')
@app.route('/index/')
def showIndex():
    category = session.query(Category).order_by(asc(Category.name))
    item = session.query(Item).order_by(asc(Item.name))
#    if 'username' not in login_session:
#        return render_template('publicrestaurants.html', restaurants=restaurants)
#    else:
    return render_template('index.html', category=category, item=item)


# create a new category
@app.route('/category/new/', methods=['GET', 'POST'])
def newCategory():
#    if 'username' not in login_session:
#        return redirect('/login')
    if request.method == 'POST':
        newCategory = Category(
            name=request.form['name']) # , user_id=login_session['user_id'])
        session.add(newCategory)
#        flash('New Category %s Successfully Created' % newCategory.name)
        session.commit()
        return redirect(url_for('showIndex'))
    else:
        return render_template('newCategory.html')



# @app.route('/restaurant/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
# def editRestaurant(restaurant_id):
#     editedRestaurant = session.query(
#         Restaurant).filter_by(id=restaurant_id).one()
# #    if 'username' not in login_session:
# #        return redirect('/login')
# #    if editedRestaurant.user_id != login_session['user_id']:
# #        return "<script>function myFunction() {alert('You are not authorized to edit this restaurant. Please create your own restaurant in order to edit.');}</script><body onload='myFunction()''>"
#     if request.method == 'POST':
#         if request.form['name']:
#             editedRestaurant.name = request.form['name']
#             flash('Restaurant Successfully Edited %s' % editedRestaurant.name)
#             return redirect(url_for('showRestaurants'))
#     else:
#         return render_template('editRestaurant.html', restaurant=editedRestaurant)
#
#
# # Delete a restaurant
# @app.route('/restaurant/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
# def deleteRestaurant(restaurant_id):
#     restaurantToDelete = session.query(
#         Restaurant).filter_by(id=restaurant_id).one()
#     if 'username' not in login_session:
#         return redirect('/login')
#     if restaurantToDelete.user_id != login_session['user_id']:
#         return "<script>function myFunction() {alert('You are not authorized to delete this restaurant. Please create your own restaurant in order to delete.');}</script><body onload='myFunction()''>"
#     if request.method == 'POST':
#         session.delete(restaurantToDelete)
#         flash('%s Successfully Deleted' % restaurantToDelete.name)
#         session.commit()
#         return redirect(url_for('showRestaurants', restaurant_id=restaurant_id))
#     else:
#         return render_template('deleteRestaurant.html', restaurant=restaurantToDelete)
#
#
# # Show a restaurant menu
# @app.route('/restaurant/<int:restaurant_id>/')
# @app.route('/restaurant/<int:restaurant_id>/menu/')
# def showMenu(restaurant_id):
#     restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
# #    creator = getUserInfo(restaurant.user_id)
#     items = session.query(MenuItem).filter_by(
#         restaurant_id=restaurant_id).all()
# #    if 'username' not in login_session or creator.id != login_session['user_id']:
# #        return render_template('publicmenu.html', items=items, restaurant=restaurant, creator=creator)
# #    else:
#     return render_template('menu.html', items=items, restaurant=restaurant, creator=creator)


# Create a new item
@app.route('/catalog/newitem/', methods=['GET', 'POST'])
def newItem():
#    if 'username' not in login_session:
#        return redirect('/login')
#    category = session.query(Category).filter_by(id=category_id).one()
#    if login_session['user_id'] != restaurant.user_id:
#        return "<script>function myFunction() {alert('You are not authorized to add menu items to this restaurant. Please create your own restaurant in order to add items.');}</script><body onload='myFunction()''>"
    category = session.query(Category).order_by(asc(Category.name))
    if request.method == 'POST':
        newItem = Item(name=request.form['name'], description=request.form['description'], category_id=request.form['category']) # , user_id=restaurant.user_id)
        session.add(newItem)
        session.commit()
#            flash('New Menu %s Item Successfully Created' % (newItem.name))
        return redirect(url_for('showIndex'))
    else:
        return render_template('newitem.html', category=category)


# # Edit a menu item
# @app.route('/catalog/<str:item_name>/edit', methods=['GET', 'POST'])
# def editItem(category_id, item_id):
# #    if 'username' not in login_session:
# #        return redirect('/login')
#     editedItem = session.query(MenuItem).filter_by(id=menu_id).one()
#     restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
# #    if login_session['user_id'] != restaurant.user_id:
# #        return "<script>function myFunction() {alert('You are not authorized to edit menu items to this restaurant. Please create your own restaurant in order to edit items.');}</script><body onload='myFunction()''>"
#     if request.method == 'POST':
#         if request.form['name']:
#             editedItem.name = request.form['name']
#         if request.form['description']:
#             editedItem.description = request.form['description']
#         if request.form['price']:
#             editedItem.price = request.form['price']
#         if request.form['course']:
#             editedItem.course = request.form['course']
#         session.add(editedItem)
#         session.commit()
#         flash('Menu Item Successfully Edited')
#         return redirect(url_for('showItem', category_id=category_id))
#     else:
#         return render_template('edititem.html', restaurant_id=restaurant_id, menu_id=menu_id, item=editedItem)
#
#
# # Delete a menu item
# @app.route('/catalog/<str:item_name>/delete', methods=['GET', 'POST'])
# def deleteItem(category_id, item_id):
# #    if 'username' not in login_session:
# #        return redirect('/login')
#     category = session.query(Category).filter_by(id=category_id).one()
#     itemToDelete = session.query(Item).filter_by(id=item_id).one()
# #    if login_session['user_id'] != restaurant.user_id:
# #        return "<script>function myFunction() {alert('You are not authorized to delete menu items to this restaurant. Please create your own restaurant in order to delete items.');}</script><body onload='myFunction()''>"
#     if request.method == 'POST':
#         session.delete(itemToDelete)
#         session.commit()
#         flash('Menu Item Successfully Deleted')
#         return redirect(url_for('showCategory', Category_id=Category_id))
#     else:
#         return render_template('deleteItem.html', item=itemToDelete)



if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
