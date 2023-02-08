from flask import render_template,session,request,redirect,url_for,flash

from shop import app,db,bcrypt
from .forms import RegistrationForm,LoginForm
from .models import User
from shop.products.models import Addproduct,Brand,Category
from flask_login import current_user, login_required,login_user, logout_user
import os
import secrets
from PIL import Image



@app.before_first_request
def create_tables():
    db.create_all()



# def home():
#     if 'email' not in session:
#         flash("Please login ",'danger')
#         return redirect (url_for('login'))
#     return render_template('admin/index.html',title="Admin Page")


@app.route('/admin')
@login_required
def admin():
    # if 'email' not in session:
    #     flash("Please login ",'danger')
    #     return redirect (url_for('login'))
    products=Addproduct.query.all()
    return render_template('admin/index.html',title='Admin Page',products=products)



@app.route('/brands')
@login_required
def brands():
    # if 'email' not in session:
    #     flash("Please login ",'danger')
    #     return redirect (url_for('login'))
    brands=Brand.query.order_by(Brand.id.desc()).all()
 
    return render_template('admin/brand.html',title='Brand Page',brands=brands)



@app.route('/category')
@login_required
def category():
    # if 'email' not in session:
    #     flash("Please login ",'danger')
    #     return redirect (url_for('login'))
 
    categories=Category.query.order_by(Category.id.desc()).all()
    return render_template('admin/brand.html',title='categories Page',categories=categories)


def save_meme(form_profile):
    random_hex = secrets.token_hex(8)
   
    _, f_ext = os.path.splitext( form_profile.filename)
    meme_fn = random_hex + f_ext
    meme_path = os.path.join(app.root_path, 'static/profile_pics', meme_fn)
    output_size = (500,500)
    i = Image.open(form_profile)
    i.thumbnail(output_size)
    i.save(meme_path)
    return meme_fn


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        profile=request.files['profile']
        flash(f'{profile.filename} is profile')
        if profile:
            profile = save_meme(profile)
            flash(f'{profile} is profile')

            user = User(name=form.name.data,username=form.username.data, email=form.email.data, password=hashed_password,profile=profile)
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You are now able to log in', 'success')
        
            return redirect(url_for('login'))

    return render_template('admin/register.html', form=form,title="Registration Page")




@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash(f'Welcome {form.email.data},You logged in ','success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('admin'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('admin/login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))
