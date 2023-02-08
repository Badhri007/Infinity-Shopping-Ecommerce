from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import MetaData
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

from flask_uploads import IMAGES,UploadSet,configure_uploads,patch_request_class
from flask_msearch import Search
from flask_migrate import Migrate

import os



# convention = {
#     "ix": 'ix_%(column_0_label)s',
#     "uq": "uq_%(table_name)s_%(column_0_name)s",
#     "ck": "ck_%(table_name)s_%(constraint_name)s",
#     "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
#     "pk": "pk_%(table_name)s"
# }

# metadata = MetaData(naming_convention=convention)
# metadata = MetaData(naming_convention=convention, metadata=metadata)


basedir=os.path.abspath(os.path.dirname(__file__))
app=Flask(__name__)
app.config['SECRET_KEY']='abcdefghijklmnop'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'
app.config['UPLOADED_PHOTOS_DEST']=os.path.join(basedir,'static/images')
photos=UploadSet('photos',IMAGES)
configure_uploads(app,photos)
patch_request_class(app)
db=SQLAlchemy(app)
bcrypt=Bcrypt(app)

migrate=Migrate(app,db,render_as_batch=True)
login_manager=LoginManager(app)
login_manager.login_view='login'
login_manager.login_view='customerlogin'
login_manager.login_message_category='info'

search= Search()
search.init_app(app)




from shop.admin import routes
from shop.products import routes
from shop.carts import carts
from shop.customers import routes