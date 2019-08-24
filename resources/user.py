from werkzeug.security import safe_str_cmp
from flask_restful import Resource, reqparse
from blacklist import BLACKLIST
from flask_jwt_extended import (create_access_token,
                                create_refresh_token,
                                jwt_refresh_token_required,
                                get_jwt_identity,
                                jwt_required,
                                get_raw_jwt)
from models.user import UserModel


class UserRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, required=True, help="Username is required")
    parser.add_argument('password', type=str, required=True, help="Password is required")

    def post(self):
        data = UserRegister.parser.parse_args()
        if UserModel.find_by_username(data['username']):
            return {'message': 'User exist with same username'}

        user = UserModel(data['username'], data['password'])
        user = UserModel.save(user)
        # user.save()
        return {'message': 'User created successfully', 'data': user.json()}, 201


class User(Resource):

    def get(self, user_id: int):
        print('user id {}', user_id)
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        print(user.username)
        return user.json(), 200

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        user.delete()
        return {'message': 'User deleted successfully'}, 200


class UserLogin(Resource):

    @classmethod
    def post(cls):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True, help="Username is required")
        parser.add_argument('password', type=str, required=True, help="Password is required")
        data = UserRegister.parser.parse_args()
        username = data['username']
        password = data['password']
        user = UserModel.find_by_username(username)
        if user and safe_str_cmp(user.password, password):
            access_token = create_access_token(identity=user.id, fresh = True)
            refresh_token = create_refresh_token(user.id)
            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200
        return {'message': 'Invalid username or password'}, 401


class UserLogout(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']  # jwt id
        BLACKLIST.add(jti)
        return {'message': 'logout successful'}, 200


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {'access_token': new_token}, 200

