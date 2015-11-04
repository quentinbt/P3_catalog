# imports
from flask import Flask, render_template, request, redirect, jsonify, \
                  url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from flask.ext.seasurf import SeaSurf


app = Flask(__name__)


csrf = SeaSurf(app)


# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase +
                    string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@csrf.exempt
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'
                                            ), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']  # noqa
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (  # noqa
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]
    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email'\
        % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to
    # properly logout, let's strip out the information before
    # the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token  # noqa
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '  # noqa

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id, access_token)  # noqa
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showIndex'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showIndex'))


# JSON APIs to view category information
@app.route('/catalog/categories/JSON')
def categoryJSON():
    categories = session.query(Category).all()
    return jsonify(Categories=[c.serialize for c in categories])


@app.route('/catalog/items/JSON')
def ItemJSON():
    items = session.query(Item).all()
    return jsonify(ItemsInCategory=[i.serialize for i in items])


# Show all category & last item added
@app.route('/')
@app.route('/index/')
def showIndex():
    category = session.query(Category).order_by(asc(Category.name))
    item = session.query(Item).order_by(asc(Item.name))
    catitem = session.query(Category.name, Category.id,
                            Item.name.label('item_name'),
                            Item.id.label('item_id')).join(Item)
    if 'username' not in login_session:
        return render_template('publicindex.html', category=category,
                               item=item, catitem=catitem)
    else:
        return render_template('index.html', category=category,
                               item=item, catitem=catitem)


# create a new category
@app.route('/category/new/', methods=['GET', 'POST'])
def newCategory():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCategory = Category(
            name=request.form['name'],
            description=request.form['description'],
            user_id=login_session['user_id'])
        testname = session.query(Category).filter_by(
                    name=newCategory.name).first()
        if not testname:
            session.add(newCategory)
            flash('New Category %s Successfully Created' % newCategory.name)
            session.commit()
            return redirect(url_for('showIndex'))
        else:
            flash('New Category %s Already exist' % newCategory.name)
            return redirect(url_for('showIndex'))
    else:
        return render_template('newCategory.html')


# Show a category
@app.route('/catalog/<string:category_name>/')
def showCategory(category_name):
    catego = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(category_id=catego.id).all()
    return render_template('category.html', items=items,
                           category_name=category_name, category=catego)


# Edit a category
@app.route('/catalog/<string:category_name>/edit/', methods=['GET', 'POST'])  # noqa
def editCategory(category_name):
    editedCategory = session.query(Category).filter_by(
        name=category_name).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedCategory.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not auth\
        orized to edit this category. Please create your own category \
        in order to edit.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        oldname = editedCategory.name
        if request.form['name']:
            editedCategory.name = request.form['name']
        if request.form['description']:
            editedCategory.description = request.form['description']
        if oldname == editedCategory.name:
            session.add(editedCategory)
            session.commit()
            flash('Category Successfully Edited %s' % editedCategory.
                  name)
            return redirect(url_for('showIndex'))
        else:
            testname = session.query(Category).filter_by(
                name=editedCategory.name).first()
            if not testname:
                session.add(editedCategory)
                session.commit()
                flash('Category Successfully Edited %s' % editedCategory.
                      name)
                return redirect(url_for('showIndex'))
            else:
                flash('The New Category name %s Already exist'
                      % editedCategory.name)
                editedCategory.name = oldname
                return redirect(url_for('showIndex'))
    else:
        return render_template('editCategory.html',
                               category=editedCategory)


# Delete a category
@app.route('/catalog/<string:category_name>/delete/', methods=['GET', 'POST'])  # noqa
def deleteCategory(category_name):
    categoryToDelete = session.query(
        Category).filter_by(name=category_name).one()
    if 'username' not in login_session:
        return redirect('/login')
    if categoryToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not auth\
        orized to delete this category. Please create your own categor\
        y in order to delete.');}</script><body onload='myFunction()''\
        >"
    if request.method == 'POST':
        session.delete(categoryToDelete)
        flash('%s Successfully Deleted' % categoryToDelete.name)
        session.commit()
        return redirect(url_for('showIndex'))
    else:
        return render_template('deletecategory.html',
                               category=categoryToDelete)


# Show item
@app.route('/catalog/<string:category_name>/<string:item_name>/')
def showItem(category_name, item_name):
    item = session.query(Item).filter_by(name=item_name).one()
    return render_template('item.html', item=item,
                           category_name=category_name)


# Create a new item
@app.route('/catalog/newitem/', methods=['GET', 'POST'])
def newItem():
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).order_by(asc(Category.name))
    if request.method == 'POST':
        newItem = Item(name=request.form['name'],
                       description=request.form['description'],
                       category_id=request.form['category'],
                       picture=request.form['picture'],
                       user_id=login_session['user_id'])
        testname = session.query(Item).filter_by(
            name=newItem.name).first()
        if not testname:
            session.add(newItem)
            session.commit()
            flash('New Item: %s Successfully Created' % (newItem.name))
            return redirect(url_for('showIndex'))
        else:
            flash('New Item %s Already exist' % newItem.name)
            return redirect(url_for('showIndex'))
    else:
        return render_template('newitem.html', category=category)


# Edit an item
@app.route('/catalog/<string:category_name>/<string:item_name>/edit', methods=['GET', 'POST'])  # noqa
def editItem(category_name, item_name):
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(Item).filter_by(name=item_name).one()
    category = session.query(Category).order_by(asc(Category.name))
    if login_session['user_id'] != editedItem.user_id:
        return "<script>function myFunction() {alert('You are not auth\
        orized to edit items to this category. Please create your own \
        category in order to edit items.');}</script><body onload='myF\
        unction()''>"
    if request.method == 'POST':
        oldname = editedItem.name
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['category']:
            editedItem.category_id = request.form['category']
        if request.form['picture']:
            editedItem.picture = request.form['picture']
        if oldname == editedItem.name:
            session.add(editedItem)
            session.commit()
            flash('Item Successfully Edited')
            return redirect(url_for('showIndex'))
        else:
            testname = session.query(Item).filter_by(
                            name=editedItem.name).first()
            if not testname:
                session.add(editedItem)
                session.commit()
                flash('Item Successfully Edited %s'
                      % editedItem.name)
                return redirect(url_for('showIndex'))
            else:
                flash('The New Item name %s Already exist'
                      % editedItem.name)
                editedItem.name = oldname
                return redirect(url_for('showIndex'))
    else:
        return render_template('edititem.html',
                               category_name=category_name,
                               category=category,
                               item=editedItem)


# Delete an item
@app.route('/catalog/<string:category_name>/<string:item_name>/delete', methods=['GET', 'POST'])  # noqa
def deleteItem(category_name, item_name):
    if 'username' not in login_session:
        return redirect('/login')
    itemToDelete = session.query(Item).filter_by(name=item_name).one()
    if login_session['user_id'] != itemToDelete.user_id:
        return "<script>function myFunction() {alert('You are not auth\
        orized to delete this items.');}</script><body onload='myFunct\
        ion()''>"
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Item Successfully Deleted')
        return redirect(url_for('showIndex'))
    else:
        return render_template('deleteitem.html', item=itemToDelete)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
