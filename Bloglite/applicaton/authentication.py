from flask import Blueprint, render_template, redirect,url_for ,request,flash
from . import db
from .models import User
from flask_login import login_user, logout_user, login_required,current_user
from werkzeug.security import generate_password_hash, check_password_hash


authentication = Blueprint("authentication",__name__)

@authentication.route("/login",methods=["GET","POST"])
def log_in():
    if request.method=="POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password,password):
                flash("Logged in!")
                login_user(user,remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Password is incorrect', category='error')
        else:
            flash('Email does not exist',category='error')
                    
    # Render the login template when accessed via GET request
    return render_template("login.html",user=current_user)


@authentication.route("/sign-up",methods=["GET","POST"])
def sign_up():
    # If the request method is POST
    if request.method == "POST":
        # Get the form data
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        # Check if the email or username already exists in the database
        email_exist = User.query.filter_by(email=email).first()
        user_exist = User.query.filter_by(username=username).first()

        # Validate the form data
        if email_exist:
            flash('Email is already exist',category='error')
        elif user_exist:
            flash('Username is already in exist',category='error')
        elif password != confirm_password:
            flash('Password are not matching',category='error')
        elif len(username) < 3:
            flash('Username is too short',category='error')
        elif len(password) < 6:
            flash('Password is too short',category='error')
        elif len(email) < 4:
            flash("Email is invalid",category='error')
        # If the form data is valid
        else:
            # Create a new user object
            new_user = User(email=email,username=username,password=generate_password_hash(password,method='sha256'))
            # Add the user to the database
            db.session.add(new_user)
            db.session.commit()
            # Log the user in
            login_user(new_user,remember=True)
            flash('User created!')
            # Redirect the user to the home page
            return redirect(url_for('views.home'))
    # If the request method is GET
    # render the signup template
    return render_template("signup.html",user=current_user)

    
@authentication.route("/logout")
@login_required
def log_out():
    logout_user()
    return redirect(url_for("views.home"))

@authentication.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        # Get the new username and password from the form
        new_username = request.form.get("username")
        new_password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # Check if the new username is already taken
        user_exist = User.query.filter_by(username=new_username).first()
        if user_exist and user_exist != current_user:
            flash("Sorry, that username is already taken", category='error')
            return render_template("settings.html", user=current_user)
        if new_password != confirm_password:
            flash("Passwords do not match, please try again.", category='error')
            return render_template("settings.html", user=current_user)
        if len(new_username) < 3:
            flash('Username is too short',category='error')
            return render_template("settings.html", user=current_user)
        if len(new_password) < 6:
            flash('Password is too short',category='error')
            return render_template("settings.html", user=current_user)
        
        # Update the user's username and password
        current_user.username = new_username
        current_user.password = generate_password_hash(new_password, method='sha256')
        db.session.commit()

        flash("Your settings have been updated!", category='success')
        return redirect(url_for('views.home'))
    
    return render_template("settings.html", user=current_user)
