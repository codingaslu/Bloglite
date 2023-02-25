# Import necessary modules and libraries
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

# Create a SQLAlchemy object for database management
db = SQLAlchemy()

def create_app():
    # Create a Flask app instance
    app = Flask(__name__)
    # Set the secret key for the app
    app.config['SECRET_KEY'] = "perfetch"
    # Set the database URI for the app
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"

    # Initialize the SQLAlchemy object with the app
    db.init_app(app)
    # Push the app context
    app.app_context().push()
    # Import and initialize the API module
    from .resources import api
    api.init_app(app)

    # Import and register the views blueprint
    from .views import views
    app.register_blueprint(views,url_prefix="/")
    
    # Import and register the authentication blueprint
    from .authentication import authentication
    app.register_blueprint(authentication,url_prefix="/")

    # Import the models
    from .models import User,Post,Comment,Like,Follower
    # Create the database if it does not exist
    create_database(app)
    
    # Initialize the LoginManager
    login_manager = LoginManager()
    login_manager.login_view = "authentication.log_in"
    login_manager.init_app(app)
    
    # Define a user loader function for the LoginManager
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
        
    # Return the app instance
    return app

def create_database(app):
    # Check if the database file exists
    if not path.exists("applicaton/"+"database.db"):
        # Create the database tables
        db.create_all(app=app)
        print("Created database!")
