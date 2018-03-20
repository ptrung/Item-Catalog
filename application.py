#!/usr/bin/env python

from flask import Flask, render_template, request
from flask import redirect, url_for, flash, jsonify, make_response
from flask import session as login_session
import random
import string

from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import User, Base, Category, Item

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import httplib2
import json
import requests

# Flask instance
app = Flask(__name__)

# DB session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Google Client Secret
CLIENT_ID = json.loads(open('client_secrets.json', 'r')
                       .read())['web']['client_id']
APPLICATION_NAME = "Sweets Catalog"


# FLASK ROUTING
# Login Page for GConnect
@app.route('/login/')
def show_login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
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

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = get_userid(login_session['email'])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("You are now logged in as %s" % login_session['username'])
    return output


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    parturl = 'https://accounts.google.com/o/oauth2/revoke?token=%s'
    url = parturl % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = redirect(url_for('show_catalog'))
        flash("You are now logged out.")
        return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# User Helper Functions
def create_user(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def get_userinfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def get_userid(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Show the main page of the catalog (categories & latest items)
@app.route('/')
@app.route('/catalog/')
def show_catalog():
    categories = session.query(Category).all()
    latestItems = session.query(Item).order_by(
        desc(Item.timestamp)).limit(5).all()
    return render_template('showCatalog.html',
                           categories=categories, latestItems=latestItems)


# Show the items of a specific category
@app.route('/catalog/<path:category_name>/')
@app.route('/catalog/<path:category_name>/items/')
def show_category(category_name):
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(
        category=category).order_by(asc(Item.title)).limit(5)

    if 'username' not in login_session:
        return render_template(
            'showPublicCategory.html',
            categories=categories, category=category, items=items)
    else:
        return render_template(
            'showCategory.html',
            categories=categories, category=category, items=items)


# Show the description of a specific item
@app.route('/catalog/<path:category_name>/<path:item_title>')
def show_item(category_name, item_title):
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(Item).filter_by(
        category=category).filter_by(title=item_title).one()
    creator = get_userinfo(item.user_id)

    if 'username' not in login_session or \
       creator.id != login_session['user_id']:
        return render_template(
            'showPublicItem.html',
            category_name=category_name, item=item)
    else:
        return render_template(
            'showItem.html',
            category_name=category_name, item=item)


# Create a new item
@app.route('/catalog/<path:category_name>/new/', methods=['GET', 'POST'])
def new_item(category_name):
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(
        category=category).order_by(asc(Item.title)).limit(5)

    if 'username' in login_session and login_session['username'] != 'null':
        if request.method == 'POST':
            newItem = Item(title=request.form['title'],
                           description=request.form['description'],
                           category=category,
                           user_id=login_session['user_id'])
            session.add(newItem)
            session.commit()
            return redirect(url_for(
                'show_item',
                category_name=category_name, item_title=newItem.title))
        else:
            return render_template(
                'newItem.html',
                category_name=category_name)
    else:
        flash("Please log in to add an item!")
        return redirect(url_for(
            'show_category', category_name=category_name))


# Edit an existing item
@app.route('/catalog/<path:category_name>/<path:item_title>/edit/',
           methods=['GET', 'POST'])
def edit_item(category_name, item_title):
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(
        name=category_name).one()
    item = session.query(Item).filter_by(
        category=category).filter_by(title=item_title).one()

    if 'username' in login_session and login_session['username'] != 'null':
        if get_userinfo(item.user_id).id == login_session['user_id']:
            if request.method == 'POST':
                item.title = request.form['title']
                item.description = request.form['description']
                if request.form['category'] != category_name:
                    category = session.query(Category).filter_by(
                        name=request.form['category']).one()
                    item.category = category
                session.add(item)
                session.commit()
                flash('The item is updated!')
                return redirect(url_for(
                    'show_item',
                    category_name=item.category.name, item_title=item.title))
            else:
                return render_template(
                    'editItem.html',
                    category_name=category_name, item_title=item_title,
                    item=item, categories=categories)
        else:
            flash("Only the owner is allowed to edit the item!")
            return redirect(url_for(
                'show_item',
                category_name=category_name, item_title=item_title))
    else:
        flash("Please log in to edit the item!")
        return redirect(url_for(
            'show_item',
            category_name=category_name, item_title=item_title))


# Delete an existing item
@app.route('/catalog/<path:category_name>/<path:item_title>/delete/',
           methods=['GET', 'POST'])
def delete_item(category_name, item_title):
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(Item).filter_by(
        category=category).filter_by(title=item_title).one()

    if 'username' in login_session and login_session['username'] != 'null':
        if get_userinfo(item.user_id).id == login_session['user_id']:
            if request.method == 'POST':
                session.delete(item)
                session.commit()
                flash('The item is deleted!')
                return redirect(url_for(
                    'show_category',
                    category_name=category_name))
            else:
                return render_template(
                    'deleteItem.html',
                    category_name=category_name, item_title=item_title)
        else:
            flash("Only the owner is allowed to delete the item!")
            return redirect(url_for(
                'show_item',
                category_name=category_name, item_title=item_title))
    else:
        flash("Please log in to delete the item!")
        return redirect(url_for(
            'show_item',
            category_name=category_name, item_title=item_title))


# JSON APIs to view catalog data
@app.route('/catalog.json')
def catalogJSON():
    categories = session.query(Category).all()
    dict = [c.serialize for c in categories]
    for c in range(len(dict)):
        items = [i.serialize for i in session.query(Item).filter_by(
            category_id=dict[c]["id"]).all()]
        if items:
            dict[c]["Item"] = items
    return jsonify(Category=dict)


@app.route('/categories.json')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(Categories=[c.serialize for c in categories])


@app.route('/catalog/<path:category_name>.json')
def categoryItemsJSON(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(
        category=category).order_by(asc(Item.title)).all()
    return jsonify(Items=[i.serialize for i in items])


@app.route('/catalog/<path:category_name>/<path:item_title>.json')
def catalogItemJSON(category_name, item_title):
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(Item).filter_by(
        category=category).filter_by(title=item_title).one()
    return jsonify(Items=item.serialize)


if __name__ == '__main__':
    app.secret_key = 'i_am_a_super_secrete_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
