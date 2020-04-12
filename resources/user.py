from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp
from models.user import UserModel
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    fresh_jwt_required,
    jwt_required,
    get_raw_jwt
)
from blacklist import BLACKLIST


_user_parser = reqparse.RequestParser()
_user_parser.add_argument(
    'username',
    type=str,
    required=True,
    help="esse campo é obrigario"
)
_user_parser.add_argument(
    'password',
    type=str,
    required=True,
    help="esse campo é obrigario"
)


class UserRegister(Resource):

    @classmethod
    def post(cls):
        data = _user_parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {"message": "user with this username already exists"}, 400
        user = UserModel(**data)
        user.save_to_db()
        return {"message": "User Created"}, 201


class User(Resource):

    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if user:
            return user.json()
        return {"message": "user not found"}, 404

    @classmethod
    @fresh_jwt_required
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if user:
            user.delete_from_db()
            return {"message": "deleted"}
        return {"message": "User not exists"}, 404


class UserLogin(Resource):

    @classmethod
    def post(cls):
        data = _user_parser.parse_args()
        user = UserModel.find_by_username(data['username'])
        if user and safe_str_cmp(user.password, data["password"]):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {"access_token": access_token, "refresh_token": refresh_token}

        return {"message": "user or password wrong"}, 401


class UserLogout(Resource):

    @classmethod
    @jwt_required
    def post(cls):
        jti = get_raw_jwt()['jti']  # wti = identificador unico do token
        BLACKLIST.add(jti)
        return {"message": "deslogado com sucesso"}


class TokenRefresh(Resource):

    @classmethod
    @jwt_refresh_token_required
    def post(cls):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}
