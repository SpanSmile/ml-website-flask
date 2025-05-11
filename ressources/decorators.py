from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.authority != 0:
            flash("You do not have permission to access this page.", category='danger')
            return redirect(url_for('home_page'))
        return f(*args, **kwargs)
    return decorated_function

def admin_or_teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.authority not in [0, 1]:
            flash("You do not have permission to access this page.", category='danger')
            return redirect(url_for('home_page'))
        return f(*args, **kwargs)
    return decorated_function