from ressources import db, app, bcrypt, login_manager
from flask_login import UserMixin # this contains predetermined calls that we need in login_manager along with login_manager check https://flask-login.readthedocs.io/en/latest/#how-it-works fpr more info

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(length=20), unique=True, nullable=False)
    email_address = db.Column(db.String(length=80), unique=True, nullable=False)
    authority = db.Column(db.Integer, nullable=False)
    password_hash = db.Column(db.String(length=60), nullable=False)
    exercices = db.relationship('Exercise', backref='owned_user', lazy=True)
    
    @property
    def password(self):
        return self.password
    
    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')
        
    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

class Exercise(db.Model):
    id = db.Column(db.Integer(), primary_key = True, nullable=False)
    name = db.Column(db.String(length=30), nullable=False, unique=True)
    subject = db.Column(db.String(length=50), nullable=False)
    description = db.Column(db.String(), nullable=False, unique=False)
    content = db.Column(db.String(), nullable=False)
    author = db.Column(db.Integer(), db.ForeignKey('user.id'))
    
    def __repr__(self):
        return f'Exercise name: {self.name}'

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.String(1024), nullable=False)

    
    def __repr__(self):
        return f'Item {self.name}'

app.app_context().push() # This is needed when we want to create a new database when we run the code db.create_all() we need to push context first