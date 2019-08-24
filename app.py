import os
from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from blacklist import BLACKLIST
# from security import authenticate, identity
from resources.user import UserRegister, User, UserLogin, TokenRefresh, UserLogout
from resources.item import Item, ItemList
from resources.store import Store, StoreList

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "data.db"))

app = Flask(__name__)
app.secret_key = '@cc3ss'
app.config['SQLALCHEMY_DATABASE_URI'] = database_file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
api = Api(app)

jwt = JWTManager(app) # /auth


@jwt.user_claims_loader
def add_claims_to_jwt(identity):
    if identity == 1:
        return {'is_admin': True}
    else:
        return {'is_admin': False}


@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({
        'description': 'The token has expired.',
        'error': 'token_expired'
    }), 401


@jwt.invalid_token_loader  # called when the token is not an actual JWT
def invalid_token_callback(error):
    return jsonify({
        'description': 'Signature verification failed.',
        'error': 'Invalid token'
    }), 401


@jwt.unauthorized_loader # called when JWT is not sent at all.
def unauthorized_access():
    return jsonify({
        'description': 'Signature verification failed.',
        'error': 'Invalid token'
    }), 401


@jwt.needs_fresh_token_loader  # called when a non-fresh token is sent.
def fresh_token_required():
    return jsonify({
        'description': 'Fresh token is required.',
        'error': 'refresh_token_required'
    }), 401


@jwt.revoked_token_loader # called when a token is no longer valid
def revoked_token_callback():
    return jsonify({
        'description': 'Token has been revoked.',
        'error': 'token_revoked'
    }), 401


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    return decrypted_token['jti'] in BLACKLIST


@app.before_first_request
def create_tables():
    db.create_all()


api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(UserRegister, '/register')
api.add_resource(Store, '/store/<string:name>')
api.add_resource(StoreList, '/stores')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')
api.add_resource(TokenRefresh, '/refresh-token')

if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run(port=5000, debug=True)

