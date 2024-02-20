from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta, datetime
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)

app.secret_key = "test2"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# the amount of time befor they have to login again
app.permanent_session_lifetime = timedelta(minutes = 55) 

db = SQLAlchemy(app)    

class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))
    email = db.Column(db.String(100))
    
    def __init__(self, email, first_name, last_name, username, password):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.password = password
        
class G_list(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    email = db.Column(db.String(100), db.ForeignKey('users.email'), nullable=False)
    item_name = db.Column(db.String(100))
    item_amount = db.Column(db.Integer)
    gotten = db.Column(db.Boolean(100))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    group_id = db.Column(db.Integer)

    def __init__(self, email, item_name, item_amount, gotten, group_id):
        self.email = email
        self.item_name = item_name
        self.item_amount = item_amount
        self.gotten = gotten
        self.group_id = group_id

@app.route("/")
def base():
    # base/home page
    # have a bar for them to navigate fast
    print("home")
    return render_template("homepage.html")

@app.route("/home")
def home():
    # base/home page
    # have a bar for them to navigate fast
    print("home")
    return render_template("homepage.html")

# ------------------------- Done -----------------------------#
@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        print('post')
        print('test 1')
        reg_firstname = request.form["FirstName"]
        reg_lastname = request.form["LastName"]
        reg_password = request.form["password"]
        reg_username = request.form["username"]
        reg_email = request.form["email"]
        print("reg_email: ", reg_email)
        found_user = users.query.filter_by(email = reg_email).first()
        # check if the user is already added
        if found_user:
            print("email in use")
            flash ("Email in use")
            flash ("Try and login :)")
            return render_template("register.html")
        else:
            # creating the class for the user
            print("new user")
            usr = users(reg_email, reg_firstname, reg_lastname, reg_username, reg_password)
            # add to sql server
            db.session.add(usr)
            # commiting the add
            db.session.commit()
            print('user added')
            return render_template("login.html")
    else:
        # check if use is in session (already login)
        if "email" in session:
            flash ("Already Logged In!")
            return redirect(url_for("user"))
        else:
            print('not post')
            return render_template("register.html")


# ------------------------- Done -----------------------------#
@app.route("/profile", methods=["POST", "GET"])
def user_profile():
    ses_email = session.get("email")
    user = users.query.filter_by(email = ses_email).first()
    if request.method == "POST":
        if "email" in session:
            if 'FirstName' in request.form:
                reg_firstname = request.form["FirstName"]
                print("First Name")
                print(request.form["FirstName"])
                print(user.first_name)
                user.first_name = reg_firstname

            elif 'LastName' in request.form:
                reg_lastname = request.form["LastName"]
                user.last_name = reg_lastname

            elif 'password' in request.form:
                reg_password = request.form["password"]
                user.password = reg_password

            elif 'username' in request.form:
                reg_username = request.form["username"]
                user.username = reg_username

            elif 'email' in request.form:
                reg_email = request.form["email"]
                user.email = reg_email

            db.session.commit()
            flash("Profile Updated") 
        else:
            print("need to login")
            return render_template("login.html")
    return render_template("profile.html")
# ------------------------- Done -----------------------------#
@app.route("/edit_item", methods=["POST", "GET"])
def edit_item():
    print('edit item')
    if request.method == "POST":
        email = session.get('email')
        item_id = request.form["edit_item_id"]
        item_found =G_list.query.filter_by(id = item_id).first()
        item_name = item_found.item_name
        item_amount = item_found.item_amount
        group_id = item_found.group_id
        if 'edit_item_name' in request.form:
            item_name = request.form["edit_item_name"]
        
        if 'edit_item_amount' in request.form:
            item_amount = request.form["edit_item_amount"]
        
        if 'edit_group_id' in request.form:
            group_id = request.form["edit_group_id"]
        
        if request.form.get('edit_Gotten') == 'on':
            gotten = True
        else:
            gotten = False

        if request.form.get('delete_item') == 'on':
            db.session.delete(item_found)
            db.session.commit()
        else:
            item_found.item_name = item_name
            item_found.item_amount = item_amount
            item_found.group_id = group_id
            item_found.gotten = gotten
            # commiting the add
            db.session.commit()
        
    
    return redirect(url_for("user_list"))

# ------------------------- Done --------------------------#
@app.route("/user_list", methods=["POST", "GET"])
def user_list():
    if "email" in session:
        if request.method == "POST":
            # this is to add items to the list
            email = session.get('email')
            
            found_user = users.query.filter_by(email = email).first()
            print(email)
            if 'item_name' in request.form:
                item_name = request.form["item_name"]
            
            if 'item_amount' in request.form:
                item_amount = request.form["item_amount"]
            else:
                item_amount = None
            
            if 'group_id' in request.form:
                group_id = request.form["group_id"]
            else:
                group_id = 0
            
            if request.form.get('gotten') == 'on':
                gotten = True
            else:
                gotten = False
            
            item = G_list(email, item_name, item_amount, gotten, group_id)
            # add to sql server
            db.session.add(item)
            # commiting the add
            db.session.commit()

            # edit items on the list:
            session_email = session.get('email')
            found_user = users.query.filter_by(email = session_email).first()
            # get the first and last name to print out for the user 
            f_name = found_user.first_name
            l_name = found_user.last_name
            print(session_email)
            data = G_list.query.filter_by(email = session_email).all()
            results_as_dicts = [data.__dict__ for data in data]
            print(results_as_dicts)
            data = [{key: value for key, value in item.items() if not key.startswith('_')} for item in results_as_dicts]
            print(data)

            return render_template('list.html', data=data)
        else:   
            session_email = session.get('email')
            found_user = users.query.filter_by(email = session_email).first()
            # get the first and last name to print out for the user 
            f_name = found_user.first_name
            l_name = found_user.last_name
            print(session_email)
            data = G_list.query.filter_by(email = session_email).all()
            results_as_dicts = [data.__dict__ for data in data]
            print(results_as_dicts)
            data = [{key: value for key, value in item.items() if not key.startswith('_')} for item in results_as_dicts]
            
            return render_template('list.html', data=data)


            # pull the data from the user

                # present the data to the user
                
                #--------------------------------------------------------#
                # need to have it so that we can add what we need for the user
            

        # we render what we need 
        return render_template("user_list.html")
    else:
        
        flash("Please Login First")
        return redirect(url_for("login"))

@app.route("/<list_number>", methods=["POST", "GET"])
def show_list(list_number):
    print('list number 1', list_number)
    if request.method == "POST":
        print('post')
        print('adding items')
        print('list number 2', list_number)
        if 'item_name' in request.form:
            item_name = request.form["item_name"]
        
        if 'item_amount' in request.form:
            item_amount = request.form["item_amount"]
        else:
            item_amount = None
        if request.form.get('gotten') == 'on':
            gotten = True
        else:
            gotten = False

        item = G_list("guest", item_name, item_amount, gotten, list_number)
            # add to sql server
        db.session.add(item)
        # commiting the add
        db.session.commit()
        data = G_list.query.filter_by(group_id = list_number).all()
        results_as_dicts = [data.__dict__ for data in data]
        print(results_as_dicts)
        data = [{key: value for key, value in item.items() if not key.startswith('_')} for item in results_as_dicts]
        
        print('something2')
        print(list_number)
        return render_template('guest_list.html', data=data, list_number= list_number)
    else:
        data = G_list.query.filter_by(group_id = list_number).all()
        results_as_dicts = [data.__dict__ for data in data]
        print(results_as_dicts)
        data = [{key: value for key, value in item.items() if not key.startswith('_')} for item in results_as_dicts]
        
        print('something1')
        return render_template('guest_list.html', data=data, list_number= list_number)

@app.route("/edit_item_guest/<list_number>", methods=["POST", "GET"])
def edit_item_guest(list_number):
    print()
    print('in edit')
    if request.method == "POST":
        email = 'Guest'
        item_id = request.form["edit_item_id"]
        item_found =G_list.query.filter_by(id = item_id).first()
        item_name = item_found.item_name
        item_amount = item_found.item_amount
        group_id = item_found.group_id
        if 'edit_item_name' in request.form:
            item_name = request.form["edit_item_name"]
        
        if 'edit_item_amount' in request.form:
            item_amount = request.form["edit_item_amount"]
        
        if 'edit_group_id' in request.form:
            group_id = request.form["edit_group_id"]
        
        if request.form.get('edit_Gotten') == 'on':
            gotten = True
        else:
            gotten = False

        if request.form.get('delete_item') == 'on':
            db.session.delete(item_found)
            db.session.commit()
        else:
            item_found.item_name = item_name
            item_found.item_amount = item_amount
            item_found.group_id = group_id
            item_found.gotten = gotten
            # commiting the add
            db.session.commit()
        
    
    return redirect(url_for("show_list", list_number = list_number))

# ------------------------- Done -----------------------------#
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        
        login_email = request.form["email"]
        login_password = request.form["password"]
        print(login_email)
        found_user = users.query.filter_by(email = login_email).first()
        print("found user: ", found_user)
        
        if found_user:
            print("found user")
            user_check = users.query.filter_by(email= login_email, password=login_password).first()
            session.permanent = True
            session["email"] = login_email
            return redirect(url_for('user_list')) #-----------------------------add url for redirect---------------------------#
            
        else:
            flash ("Incorrect Password")
            return render_template("login.html")
        
    else:
        # log user out if they are trying to login
        session.pop("email", None)
        # if not go to login page
        return render_template("login.html")

# ------------------------- Done -----------------------------#
@app.route("/logout")
def logout():
    # remove user for session
    print(session)
    flash("Logout successful", "info")
    session.pop("email", None)
    print(session)
    # redirect user to the login page
    return redirect(url_for("login"))

if __name__== "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)