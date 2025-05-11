from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from ressources.jinja_helpers import get_authority_label
from flask_mail import Mail

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(basedir, 'instance', 'database.db')}"
app.config["SECRET_KEY"] = '61f249e58305f7ade79019ad'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.googlemail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'your_email@gmail.com')

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login_page'  # Redirect to login page if not authenticated
login_manager.login_message_category = 'danger'  # Message category for the flash message danger means it's in read
mail = Mail(app)

app.jinja_env.globals.update(get_authority_label=get_authority_label)
from ressources import routes # this needs to be here to execute the code after importing everything
from ressources.routes import code_server  # Import the route
# Register your routes
app.register_blueprint(code_server)