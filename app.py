import os
from numpy import arange
from functools import wraps
from flask import Flask, render_template, redirect, request, url_for, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from passlib.hash import pbkdf2_sha256
from os import path
if path.exists("env.py"):
    import env


app = Flask(__name__)


app.config["MONGO_DBNAME"] = 'CanShare'
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.secret_key = "B,t=u0W};gBf{DnBClV8/BwiW[1k~7EEzoiv(1Ng'*1k!^R,4sd\
                 |4-[:8:_t4c8"
mongo = PyMongo(app)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Log In setup ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def check_logged_in(func):
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        if 'logged-in' in session:
            return(func(*args, **kwargs))
        else:
            return render_template('nologin.html')
    return wrapped_function


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template('register.html')
    elif request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['type']
        _hash = pbkdf2_sha256.hash(password)
        mongo.db.users.insert_one({
            'username': username,
            'email': email,
            'password': _hash,
            'type': user_type
        })
        return redirect(url_for('login'))


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template('login.html')
    elif request.method == "POST":
        email = request.form['email']
        user = mongo.db.users.find_one({'email': email})    # if else statment to check if a user is regitsered or not if not redidrect
        user_password = user['password']
        form_password = request.form['password']
        if pbkdf2_sha256.verify(form_password, user_password):
            session['logged-in'] = True
            session['username'] = user['username']
            session['email'] = email
            session['usertype'] = user['type']
        else:
            return "login error"                                   # create login error page
        return redirect(url_for('homeLoggedIn'))
        # return render_template('beerceller_loggedin.html', user_type=session['username'])


@app.route('/logout')
@check_logged_in
def logout():
    session.pop('logged-in', None)
    session.pop('email', None)
    session.pop('usertype', None)
    return redirect(url_for('home'))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Page Routes ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



def calculate(_id):  # id of the beer
    # 1. variable run mogo find all on the ratings table with the canid as search param
    # results = list(mongo.db.ratings.find({'_id': ObjectId(res['beer_type'])})
    # 2. calculate the average 
    #2.1 create vatrable called total = 0
    #2.2 for varaible in results 
    # total += vaiable['rating']
    # 2.3 ouside for loop divide total by len(results)
    # 3. return that value


# @app.route('/vote/<can_id>/<rating>')
# def vote(can_id, rating):
    return 'hello world'
    # results = mongo.db.ratings.find_one({'canId': ObjectId(can_id), 'userId': ObjectId(session userId)}
    # check if user has alredy voted on the can
    # 2. len(results) if len results 0 user has not voted 
    # insert(rating canid and userid) if rating is 1 return thumbs up else return thumbs down
    # else len results is not 0 means user has voted results[rating] if results[rating] == to rating delete results[_id] using def delete return disable both unchecked from java
    # if results[rating] != results update ratings =0 reuturn the name of the icon that needs to be checked
    


@app.route('/')
@app.route('/home')
def home():
    return render_template("beerceller.html")


@app.route('/homeLoggedIn')
@check_logged_in
def homeLoggedIn():
    # if session['usertype']: return admin panel,
    results = list(mongo.db.cansAndBottleInfo.find())
    for res in results:
        beer_type = mongo.db.type.find_one({'_id': ObjectId(res['beer_type'])})
        res['beer_name'] = beer_type['type']
        # average = calculate(res['_id'])for each results call the calulate function and pass in the can_id
        # res['average'] = average
    return render_template("beerceller_loggedin.html",
                           caninfo=results,
                           background='background_image_landing',
                           username=session['username'])


@app.route('/can_info/<can_id>')
@check_logged_in
def can_info(can_id):
    results = mongo.db.cansAndBottleInfo.find_one({'_id': ObjectId(can_id)})
    _beer_type = mongo.db.type.find_one({'_id': ObjectId(results['beer_type'])})
    # average = calculate(results['_id'])for each results call the calulate function and pass in the can_id
    # res['average'] = average
    print(_beer_type)
    return render_template('caninfo.html', caninfo=results,
                           beer_type=_beer_type)


@app.route('/help')
def help():
    return render_template('help.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/topshelf')
def topshelf():
    return render_template('topshelf.html')


@app.route('/friends')
def friends():
    return render_template('friends.html')


# CREATE
@app.route("/add_beer", methods=["GET", "POST"])
@check_logged_in
def add_beer():
    if request.method == 'GET':
        return render_template('addnewbeer.html',
                               typesofbeer=mongo.db.type.find(),
                               abvnumber=arange(0, 200, 1),
                               price=arange(0, 200, 1),
                               background='background_image_create')
    if request.method == 'POST':
        # GET THE DATA FROM MY FORM (COMING FROM THE CLIENT)
        cans = mongo.db.cansAndBottleInfo
        form = request.form.to_dict()
        form['beer_type'] = ObjectId(form['beer_type'])
        cans.insert_one(form)
        return redirect(url_for('home'))


# UPDATE
@app.route("/edit_beer/<can_id>", methods=['GET', 'POST'])
@check_logged_in
def edit_beer(can_id):
    if request.method == 'GET':
        _the_can = mongo.db.cansAndBottleInfo.find_one({'_id':
                                                        ObjectId(can_id)})
        variety_of_beer = mongo.db.type.find()
        variety_of_beer_list = [beerlist for beerlist in variety_of_beer]
        return render_template('editbeer.html', the_can=_the_can,
                               abvnumber=arange(0, 200, 1),
                               varietyofbeer=variety_of_beer_list,
                               price=arange(0, 200, 1))
    if request.method == 'POST':
        cans = mongo.db.cansAndBottleInfo
        cans.update({'_id': ObjectId(can_id)},
                    {
                    'name': request.form['name'],
                    'brand': request.form['brand'],
                    'beer_type': ObjectId(request.form['beer_type']),
                    'abv': request.form['abv'],
                    'vegan': request.form['vegan'],
                    'hop_type': request.form['hop_type'],
                    'malts': request.form['malts'],
                    'average_price': request.form['average_price'],
                    'where_bought': request.form['where_bought'],
                    'image_url': request.form['image_url'],
                    'review': request.form['review'],
                    })
        return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
