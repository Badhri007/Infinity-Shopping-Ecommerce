
from flask import current_app, redirect, render_template, session,url_for,flash,request
from flask_login import login_required
from shop import db,app,photos,search
from .models import Addproduct, Brand,Category
from .forms import Addproducts,SearchForm
from werkzeug.utils import secure_filename
from PIL import Image

import os
import secrets


@app.before_first_request
def create_tables():
    db.create_all()


def brands():
    brands=Brand.query.join(Addproduct,(Brand.id==Addproduct.brand_id)).all()
    return brands

def categories():
    categories=Category.query.join(Addproduct,(Category.id==Addproduct.category_id)).all()
    return categories

@app.context_processor
def layout():
    form=SearchForm()
    
    return dict(form=form)


@app.route('/',methods=['GET','POST'])
def home():
    page=request.args.get('page',type=int)
    products=Addproduct.query.filter(Addproduct.stock > 0).order_by(Addproduct.id.desc()).paginate(page=page,per_page=8)
    return render_template('products/index.html',products=products,brands=brands(),categories=categories())





@app.route('/result',methods=['GET','POST'])
@login_required
def result():
    form=SearchForm(request.form)
    if form.validate():
       searched=form.searched.data
       print(searched)
       products = Addproduct.query.filter(Addproduct.name.like('%'+ searched +'%'))
       products=products.order_by(Addproduct.name).all()
       
       return render_template("products/result.html",title='Search',form=form,searched=searched,products=products,brands=brands(),categories=categories())






@app.route('/brand/<int:id>',methods=['GET','POST'])
def get_brand(id):
    page=request.args.get('page',type=int)
    get_b=Brand.query.filter_by(id=id).first_or_404()
    brand=Addproduct.query.filter_by(brand=get_b).paginate(page=page,per_page=8)
    return render_template('products/index.html',brand=brand,brands=brands(),categories=categories(),get_b=get_b)

@app.route('/product/<int:id>',methods=['GET','POST'])
def single_page(id):
    product=Addproduct.query.get_or_404(id)
    return render_template('products/single_page.html',product=product,brands=brands(),categories=categories())



@app.route('/categories/<int:id>',methods=['GET','POST'])
def get_category(id):
    page=request.args.get('page',type=int)
    get_cat=Category.query.filter_by(id=id).first_or_404()
    get_cat_prod=Addproduct.query.filter_by(category_id=id).paginate(page=page,per_page=8)
    return render_template('products/index.html',categories=categories(),brands=brands(),get_cat_prod=get_cat_prod,get_cat=get_cat)





@app.route('/addbrand',methods=['GET','POST'])
@login_required
def addbrand():
    
    if request.method == "POST":
        
        getbrand=request.form.get("brand")
       
        brand=Brand(name=getbrand)
     
        db.session.add(brand)
        db.session.commit()
        flash(f'The Brand {getbrand} added to db','success')
        return redirect(url_for('addbrand'))
    return render_template("products/addbrand.html")

@app.route('/updatebrand/<int:id>',methods=['GET','POST'])
@login_required
def updatebrand(id):
    # if 'email' not in session:
    #     flash('Please Login','danger')
    updatebrand=Brand.query.get_or_404(id)
    brand=request.form.get('brand')
    if request.method == "POST":
        updatebrand.name=brand
        flash(f'Your brand {updatebrand.name} has been updated','success')
        db.session.commit()
        return redirect(url_for('brands'))
    return render_template('products/updatebrand.html',title='Update brand Page',updatebrand=updatebrand)

@app.route('/deletebrand/<int:id>',methods=['POST'])
@login_required
def deletebrand(id):

    brand=Brand.query.get_or_404(id)
  
    if request.method == "POST":
        db.session.delete(brand)
        db.session.commit()
        flash(f'Your brand {brand.name} has been deleted','success')
        return redirect(url_for('brands'))
    flash(f'Brand {brand.name} cant be deleted','danger')
    return redirect(url_for('admin'))



@app.route('/addcat',methods=['GET','POST'])
@login_required
def addcat():
    # if 'email' not in session:
    #     flash("Please login ",'danger')
    #     return redirect (url_for('login'))
    if request.method == "POST":
        
        getbrand=request.form.get("category")
       
        category=Category(name=getbrand)
     
        db.session.add(category)
        db.session.commit()
        flash(f'The Category {getbrand} added to db','success')
        return redirect(url_for('addcat'))
    return render_template("products/addbrand.html",category='category')


@app.route('/updatecat/<int:id>',methods=['GET','POST'])
@login_required
def updatecat(id):
    # if 'email' not in session:
    #     flash("Please login ",'danger')
    #     return redirect (url_for('login'))
    updatecat=Category.query.get_or_404(id)
    category=request.form.get('category')
    if request.method == "POST":
        updatecat.name=category
        flash(f'Your category {updatecat.name} has been updated','success')
        db.session.commit()
        return redirect(url_for('category'))
    return render_template('products/updatebrand.html',title='Update Category Page',updatecat=updatecat)


@app.route('/deletecategory/<int:id>',methods=['POST'])
@login_required
def deletecategory(id):
    # if 'email' not in session:
    #     flash("Please login ",'danger')
    #     return redirect (url_for('login'))

    category=Category.query.get_or_404(id)
  
    if request.method == "POST":
        db.session.delete(category)
        db.session.commit()
        flash(f'Your category {category.name} has been deleted','success')
        return redirect(url_for('category'))
    flash(f'category {category.name} cant be deleted','danger')
    return redirect(url_for('admin'))




def save_meme(form_image):
    random_hex = secrets.token_hex(8)
   
    _, f_ext = os.path.splitext( form_image.filename)
    meme_fn = random_hex + f_ext
    meme_path = os.path.join(app.root_path, 'static/images', meme_fn)
    output_size = (200,200)
    i = Image.open(form_image)
    i.thumbnail(output_size)
    i.save(meme_path)
    return meme_fn



@app.route('/addproduct',methods=['GET','POST'])
@login_required
def addproduct():
    # if 'email' not in session:
    #     flash("Please login ",'danger')
    #     return redirect (url_for('login'))

    brands=Brand.query.all()
    categories=Category.query.all()
    form=Addproducts(request.form)
   
    if request.method =="POST" :
         
            name=form.name.data
     
            price=form.price.data
            discount=form.discount.data
            stock=form.stock.data
            colors=form.colors.data
            desc=form.description.data
            brand=request.form['brand']
            brand_id= db.session.query(Brand.id).filter_by(name=brand).one().id
          
            flash(f'{brand_id} is BRAND')
            category=request.form['category']
            
            category_id=Category.query.filter_by(name=category).one().id
            flash(f'{category_id} is category')

            image_1=request.files['image_1']
            flash(f'{image_1.filename} is image 1')
            if image_1:
                image_1 = save_meme(image_1)
                flash(f'{image_1} is Image1')

            image_2=request.files['image_2']
            if image_2 :
                image_2 = save_meme(image_2)
                flash(f'{image_2} is Image2')

            image_3=request.files['image_3']
            if image_3 :
                image_3 = save_meme(image_3)
                flash(f'{image_3} is Image3')
      
             

            addpro=Addproduct(name=name,price=price,discount=discount,stock=stock,colors=colors,desc=desc,brand_id=brand_id,category_id=category_id,image_1=image_1,image_2=image_2,image_3=image_3)
        
            db.session.add(addpro)
            db.session.commit()
            flash(f'Product {name} has added to db','success')
            return redirect(url_for('addproduct'))
       

    
    return render_template('products/addproduct.html',title="Add Product Page",form=form,brands=brands,categories=categories)
    

    
@app.route('/updateproduct/<int:id>',methods=['GET','POST'])
@login_required
def updateproduct(id):
    # if 'email' not in session:
    #     flash("Please login ",'danger')
    #     return redirect (url_for('login'))

    brands=Brand.query.all()
    categories=Category.query.all()
    product=Addproduct.query.get_or_404(id)
    brand=request.form.get('brand')
    category=request.form.get('category')

    form=Addproducts(request.form)
   
    if request.method =="POST" :
        product.name=form.name.data
        product.price=form.price.data
        product.discount=form.discount.data
        product.stock=form.stock.data
        product.brand_id=brand
        product.category_id=category
        product.colors=form.colors.data
        product.desc=form.description.data
        if request.files['image_1']:
            try:
                os.unlink(os.path.join(current_app.root_path,"static/images/"+product.image_1))
                image_1=request.files['image_1']
                product.image_1=save_meme(image_1)
            except:
                image_1=request.files['image_1']
                product.image_1=save_meme(image_1)

        if request.files['image_2']:
            try:
                os.unlink(os.path.join(current_app.root_path,"static/images/"+product.image_2))
                image_2=request.files['image_2']
                product.image_2=save_meme(image_2)
            except:
                image_2=request.files['image_2']
                product.image_2=save_meme(image_2)

        if request.files['image_3']:
            try:
                os.unlink(os.path.join(current_app.root_path,"static/images/"+product.image_3))
                image_3=request.files['image_3']
                product.image_3=save_meme(image_3)
            except:
                image_3=request.files['image_3']
                product.image_3=save_meme(image_3)






        db.session.commit()
        flash(f'Your Product {product.name} gets updated','success')
        return redirect(url_for('admin'))
    
    form.name.data=product.name
    form.price.data=product.price
    form.discount.data=product.discount
    form.stock.data= product.stock
    form.colors.data= product.colors
    form.description.data=product.desc

    return render_template('products/updateproduct.html',title="Update Product Page",form=form,brands=brands,categories=categories,product=product)


@app.route('/deleteproduct/<int:id>',methods=['POST'])
@login_required
def deleteproduct(id):
    # if 'email' not in session:
    #     flash("Please login ",'danger')
    #     return redirect (url_for('login'))
    product=Addproduct.query.get(id)
    if request.method =="POST":
        try:
            os.unlink(os.path.join(current_app.root_path,"static/images/"+product.image_1))
            os.unlink(os.path.join(current_app.root_path,"static/images/"+product.image_2))
            os.unlink(os.path.join(current_app.root_path,"static/images/"+product.image_3))
        except Exception as e:
            print(e)

        db.session.delete(product)
        db.session.commit()
        flash(f'Product {product.name} deleted successfully','success')
        return redirect(url_for('admin'))
    flash(f'Product couldnot be deleted','danger')
    return redirect(url_for('admin'))