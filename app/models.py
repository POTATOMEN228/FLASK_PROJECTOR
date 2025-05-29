from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    about_me = db.Column(db.Text, default="")
    profile_image = db.Column(db.String(120), default="default.png")

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    short_description = db.Column(db.String(200), nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(100), default='default.jpg')
    category = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_ai = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref='recipes')