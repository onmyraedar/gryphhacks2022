from coterieapp import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Model):

    user_id = db.Column(db.Integer, primary_key=True)

    # Login information
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    # Columns associated with OAuth2
    token = db.Column(db.String(500))
    refresh_token = db.Column(db.String(500))
    token_uri = db.Column(db.String(500))
    client_id = db.Column(db.String(500))
    client_secret = db.Column(db.String(500))
    scopes = db.Column(db.String(500))
    authorized = db.Column(db.Boolean)

    # Data retrieved
    data_retrieved = db.Column(db.Boolean)

    # Has existing profile
    existing_profile = db.Column(db.Boolean)

    def __repr__(self):
        return f"User('{self.user_id}', '{self.username}')"

