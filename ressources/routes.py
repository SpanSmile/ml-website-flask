from ressources import app
from ressources.job_template import yaml_template
from flask import render_template, redirect, url_for, flash, request, Response, Blueprint
from ressources.models import User, Exercise, Contact
from ressources.forms import EditUserForm, LoginForm, ExerciseForm, CreateUserForm, ContactUs, SubmitJobForm
from ressources import db
from flask_login import login_user, current_user, logout_user, login_required
from ressources.decorators import admin_required, admin_or_teacher_required
from flask_paginate import Pagination, get_page_parameter
import requests
import yaml
import os
from jinja2 import Environment, select_autoescape, Template
from urllib.parse import urljoin
import websocket
from kubernetes import client, config
from kubernetes.client.rest import ApiException

env = Environment(autoescape=select_autoescape())

config_path = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(config_path, "rke2.yaml")
config.load_kube_config(config_file=path)

@app.route("/home")
def home_page():
    return render_template('home.html')

@app.route("/login", methods = ['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            login_user(attempted_user) # This is very important!!! if you use this you can have the information about the user so you can show them in the html
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('home_page'))
        else:
            flash('Username and password are not matching! Please try again', category='danger')
            return render_template('login.html', form=form)
        
    return render_template('login.html', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home_page'))

# New feature route
@app.route('/about_page', methods = ['GET', 'POST'])
def about_page():
    form = ContactUs()
    if form.validate_on_submit():
        message_to_us = Contact(name=form.name.data,
                              email=form.email.data,
                              message=form.message.data)
        db.session.add(message_to_us)
        db.session.commit()
        
        return redirect(url_for('about_page')) # calls the function market_page
    
    if form.errors != {}: # If there's no errors in the validation phase
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a message: {err_msg}', category='danger')
        return render_template('about.html', form=form)
    return render_template('about.html',form=form)

# Exercises page

from flask import request
from flask_paginate import Pagination, get_page_parameter

@app.route("/exercises", methods=['GET', 'POST'])
@login_required
def exercise_page():
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 5
    offset = (page - 1) * per_page
    
    exercises = Exercise.query.order_by(Exercise.id).offset(offset).limit(per_page).all()
    total = Exercise.query.count()
    
    authors = {}
    for exercise in exercises:
        author_id = exercise.author
        author = User.query.get(author_id)
        if author:
            authors[exercise.id] = author.username
        else:
            authors[exercise.id] = "Unknown"
    
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')
    
    return render_template('exercises.html', 
                           exercises=exercises, 
                           authors=authors, 
                           author_id=author_id,
                           pagination=pagination)
    
@app.route('/view_exercise/<int:id>')
@login_required
def view_exercise_page(id):
    exercise_to_view = Exercise.query.get_or_404(id)
    author_id = exercise_to_view.author
    author = User.query.get(author_id)
    author_name =''
    print(author)
    if author:
        author_name = author.username
    else:
        author_name = "Unknown"
    return render_template('view_exercise_page.html', exercise=exercise_to_view, author=author_name)


@app.route("/create_exercise", methods=['GET', 'POST'])
@login_required
@admin_or_teacher_required
def create_exercise_page():
    form = ExerciseForm()
    if current_user.is_authenticated:
        user = current_user.get_id()
    else:
        user = 0  # or 'some fake value', whatever
    
    if form.validate_on_submit():
        exercise_to_create = Exercise(
            name=form.exercise_name.data,
            subject=form.subject.data,
            description=form.description.data,
            content=form.content.data,
            author=user
        )
        db.session.add(exercise_to_create)
        db.session.commit()
        flash('Exercise created successfully!', category='success')
        return redirect(url_for('exercise_page'))  # Adjust the redirect as necessary
    
    if form.errors:
        for err_msg in form.errors.values():
            flash(f'There was an error with creating an exercise: {err_msg}', category='danger')
    
    return render_template('create_exercise.html', form=form)

@app.route('/edit_exercise/<int:id>', methods = ['GET', 'POST'])
@login_required #suprisingly so easy to block access to pages without login
@admin_or_teacher_required
def edit_exercise_page(id):
    exercise_to_update = Exercise.query.get_or_404(id)
    form = ExerciseForm()
    
    if form.validate_on_submit():
        exercise_to_update.name = form.exercise_name.data
        exercise_to_update.subject = form.subject.data
        exercise_to_update.description = form.description.data
        exercise_to_update.content = form.content.data
        exercise_to_update.author = current_user.id  # Use current_user.id directly
        db.session.commit()  # No need to add, just commit the changes
        flash("Exercise updated successfully", "success")
        return redirect(url_for('exercise_page'))
    
    # Pre-populate form fields
    form.exercise_name.data = exercise_to_update.name
    form.subject.data = exercise_to_update.subject
    form.description.data = exercise_to_update.description
    form.content.data = exercise_to_update.content # calls the function exercise_page
    
    if form.errors != {}: # If there's no errors in the validation phase
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')
        return render_template('edit_exercise.html', form=form)
    
    return render_template('edit_exercise.html', form=form) # calls the function exercise_page

@app.route('/delete_exercise/<int:id>')
@login_required
@admin_or_teacher_required
def delete_exercise(id):
    exercise_to_delete = Exercise.query.get_or_404(id)
    try:
        db.session.delete(exercise_to_delete)
        db.session.commit()
        flash(f"{exercise_to_delete.name} deleted successfully", category='success')
        return redirect(url_for('exercise_page'))
    except:
        return  flash(f'Exercise failed to be deleted', category='danger')

# Users page

@app.route("/users", methods=['GET', 'POST'])
@login_required
@admin_required
def user_page():
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 5  # You can adjust this number as needed
    offset = (page - 1) * per_page
    
    users = User.query.order_by(User.id).offset(offset).limit(per_page).all()
    total = User.query.count()
    
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')
    
    return render_template('users.html', 
                           users=users, 
                           pagination=pagination)

@app.route("/create_user", methods = ['GET', 'POST'])
@login_required
@admin_required
def create_user_page():
    form = CreateUserForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              authority=form.authority.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        return redirect(url_for('user_page')) # calls the function home_page
    
    if form.errors != {}: # If there's no errors in the validation phase
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')
        return render_template('create_user.html', form=form)
    
    return render_template('create_user.html', form=form)

@app.route('/edit_user/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user_page(id):
    user_to_update = User.query.get_or_404(id)
    form = EditUserForm(current_user=user_to_update)
    
    if form.validate_on_submit():
        user_to_update.username = form.username.data
        user_to_update.email_address = form.email_address.data
        user_to_update.authority = form.authority.data

        # Check if new password is provided
        if form.password1.data and form.password2.data:
            user_to_update.password = form.password1.data

        db.session.commit()
        flash("User updated successfully", category='success')
        return redirect(url_for('user_page')) 

    if form.errors:
        for err_msg in form.errors.values():
            flash(f'There was an error with updating the user: {err_msg}', category='danger')

    form.username.data = user_to_update.username
    form.email_address.data = user_to_update.email_address
    form.authority.data = user_to_update.authority
    return render_template('edit_user.html', form=form)


@app.route('/delete_user/<int:id>')
@login_required
@admin_required
def delete_user(id):
    user_to_delete = User.query.get_or_404(id)
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        return redirect(url_for('user_page'))
    except:
        return  flash(f'User failed to be deleted', category='danger')

code_server = Blueprint('code_server', __name__)

@code_server.route('/code-server')
@login_required
def code_server_page():
    return redirect("/code-server/")  # This will redirect to the same host

# This works but has some socket issue 
# @code_server.route('/code-server/', defaults={'path': ''})
# @code_server.route('/code-server/<path:path>')
# @login_required
# def proxy_code_server(path):
#     code_server_url = f'http://vscode-python-service.default.svc.cluster.local:8080/{path}'
#     try:
#         resp = requests.get(code_server_url, stream=True)
#         resp.raise_for_status()
#     except requests.exceptions.RequestException as e:
#         return f"<h1>Error</h1><p>{str(e)}</p>", 500

#     excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
#     headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]

#     return Response(resp.content, resp.status_code, headers)

# def proxy_code_server(path):
#     app.logger.debug(f"Accessed /code-server/{path}")

@app.route("/submit_job", methods=["GET", "POST"])
@login_required
def submit_job():
    form = SubmitJobForm()
    if form.validate_on_submit():
        # Extract form data
        job_name = form.name.data
        folder_name = form.folder_name.data
        gpu_memory = form.gpu_memory.data * 1000
        image_url = form.image_url.data
        print(current_user.username)
        print(job_name)
        print(folder_name)
        print(gpu_memory)
        print(image_url)
        temp = Template(yaml_template)
        variables = {
            "job_name": f"{current_user.username}-{job_name}",
            "gpu_memory": gpu_memory,
            "image": image_url,
            "nfs_server": "192.168.164.5",
            "nfs_path": f"/srv/nfs/{current_user.username}/{folder_name}"
        }
        temp_out = temp.render(variables)
        job_manifest = yaml.safe_load(temp_out)
        core_v1 = client.CoreV1Api()
        try:
            api_response = core_v1.create_namespaced_pod(
                namespace="default", 
                body=job_manifest
            )
            print("Job created successfully. Status: %s" % str(api_response.status))
        except ApiException as e:
            print("Exception when creating job: %s\n" % e)
        flash("Job submitted successfully!", category="success")
        return redirect(url_for("submit_job"))
    else:
        return render_template('submit_job.html', form=form)