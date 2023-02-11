
from flask import current_app, redirect, render_template, session,url_for,flash,request,make_response
from flask_login import current_user, login_required, login_user, logout_user
from shop import db,app,photos,search,bcrypt
import os
import secrets
from .forms import CustomerRegistrationForm,Customerloginform,UpdateProfileForm
from .models import Register ,CustomerOrder
from werkzeug.utils import secure_filename
from PIL import Image
import stripe


publishable_key='pk_test_51MVs0UFnmLrzDL1peeKWHAlRI0D4fDQ7IvHMQqLwTeJ1UabD1NCC6CQHLiF9KukTHloA2pjaB1sAjy9PRcDnj3jQ00huOtinMZ'
stripe.api_key='sk_test_51MVs0UFnmLrzDL1pdJ6nJfIf6E4IZwpkdViMbEHgy6pyJh9MGVWEpYiBcGHXRXurBlIQQ1thUZ3bE53YAwfEBHZe004nEFkhVH'




@app.route('/payment',methods=['POST'])
@login_required
def payment():
    invoice=request.form.get('invoice')
    amount=request.form.get('amount')
    customer=stripe.Customer.create(
        email=request.form['stripeEmail'],
        source=request.form['stripeToken']
    )
    charge=stripe.Charge.create(
        customer=customer.id,
        description='Shop',
        amount=amount,
        currency='usd',
    )
    orders=CustomerOrder.query.filter_by(customer_id=current_user.id,invoice=invoice).order_by(CustomerOrder.id.desc()).first()
    orders.status='Paid'
    db.session.commit()
    return render_template('customers/thanks.html',orders=orders,invoice=invoice)



@app.route('/thanks')
def thanks():
    return render_template('customers/thanks.html')


@app.before_first_request
def create_tables():
     db.create_all()



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

@app.route('/customer/register',methods=['GET','POST'])
def customer_register():
    form=CustomerRegistrationForm()
    if form.validate_on_submit():
        profile=request.files['profile']
        flash(f'{profile.filename} is profile')
        if profile:
            profile = save_meme(profile)
            flash(f'{profile} is profile')
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            register = Register(name=form.name.data,username=form.username.data, email=form.email.data, password=hashed_password,country=form.country.data,state=form.state.data,city=form.city.data,address=form.address.data,contact=form.contact.data,zipcode=form.zipcode.data,profile=profile)
            db.session.add(register)
            db.session.commit()
            flash(f'Welcome {form.name.data} ! Thank You for Registration','success')
            return redirect(url_for('customerlogin'))
    
    return render_template('customers/register.html',form=form)


@app.route("/customer/login", methods=['GET', 'POST'])
def customerlogin():
    form = Customerloginform()
    if form.validate_on_submit():
        user = Register.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('/customers/login.html', title='Login', form=form)


@app.route("/customer/logout")
def customerlogout():
    logout_user()
    return redirect(url_for('customerlogin'))

def updatecart():
    for _key,product in session['Shoppingcart'].items():
        session.modified=True
        del product['image']
        del product['colors']
    return updatecart




@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateProfileForm()
   
    if form.validate_on_submit():
        print(form.profile.data)
        if form.profile.data:
            profile_file = save_meme(form.profile.data)
            current_user.profile = profile_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.profile)
    return render_template('customers/account.html', title='Account',
                           image_file=image_file, form=form)







@app.route('/getorder')
@login_required
def get_order():
        if current_user.is_authenticated:
                customer_id=current_user.id
                invoice=secrets.token_hex(5)
                updatecart()
                try:
                   order=CustomerOrder(invoice=invoice,customer_id=customer_id,orders=session['Shoppingcart'])
                   db.session.add(order)
                   db.session.commit()
                   session.pop('Shoppingcart')
                   flash('Your order has been placed','success')
                   return redirect(url_for('orders',invoice=invoice))
                except Exception as e:
                   print(e)
                   flash('Something is Wrong','danger')
                   return redirect(url_for('getCart'))

@app.route('/orders/<invoice>')
@login_required
def orders(invoice):
        if current_user.is_authenticated:
                grandTotal=0
                subTotal=0
                customer_id=current_user.id
                print(customer_id)
                customer=Register.query.filter_by(id=customer_id).first()
                print(customer.name)
                orders=CustomerOrder.query.filter_by(customer_id=customer_id).order_by(CustomerOrder.id.desc()).first()

                print(orders)
                for _key,product in orders.orders.items():
                        discount=(product['discount']/100) * float(product['price'])
                        subTotal+=float(product['price'])*int(product['quantity'])
                        subTotal-=discount
                        tax=("%0.2f"%(.06 * float(subTotal)))
                        grandTotal=("%.2f" %(1.06 * float(subTotal)))
        else:
                return redirect(url_for('customerlogin'))
        return render_template('customers/order.html',invoice=invoice,tax=tax,subTotal=subTotal,grandTotal=grandTotal,customer=customer,orders=orders)
            

