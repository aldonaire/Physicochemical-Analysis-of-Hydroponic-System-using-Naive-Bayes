from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path

db = SQLAlchemy()
DB_NAME = "dataset.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "hydroponicmoni"
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://hydro:hydro@localhost/capstone'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    from .views import views
    from .auth import auth
    from .hydro import hydro

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(hydro, url_prefix='/')

    from .models import Para, Predicted

    with app.app_context():
        db.create_all()

    return app


# def create_database(app):
#     if not path.exists('website/' + DB_NAME):
#         db.create_all(app=app)
#         print('A newborn db was borned!')