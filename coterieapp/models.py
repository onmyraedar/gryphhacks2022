from coterieapp import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Model, UserMixin):

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
    authorized = db.Column(db.Boolean, default=False)

    # Data has already been retrieved; has existing profile
    existing_data_profile = db.Column(db.Boolean, default=False)

    # Data filepaths
    subs_filepath = db.Column(db.String(250))
    vids_filepath = db.Column(db.String(250))

    def get_id(self):
        return self.user_id

    def __repr__(self):
        return f"User('{self.user_id}', '{self.username}')"

