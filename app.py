from flask import Flask, redirect, url_for
from flask_login import LoginManager, current_user
from models import db, User
from auth import auth_bp
from routes import main_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-this-to-a-long-random-string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rentals.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'  # type: ignore[reportAttributeAccessIssue]

@login_manager.user_loader
def load_user(uid):
    return User.query.get(int(uid))

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)