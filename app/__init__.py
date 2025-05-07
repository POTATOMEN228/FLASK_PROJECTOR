from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key_here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    csrf.init_app(app)

    from app.routes.main import main_bp
    from app.auth.routes import auth_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    # ВСТАВЛЯЕТ ИМПОРТ User ВНУТРЬ create_app пожалуйста запомни!!!!
    from app.models import User

    @app.context_processor
    def inject_user():
        user_id = session.get('user_id')
        user = User.query.get(user_id) if user_id else None
        return {'current_user': user}

    return app
