import traceback
from flask_restful import Resource, request
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    fresh_jwt_required,
    jwt_required,
    get_raw_jwt
)
from marshmallow import ValidationError
from blacklist import BLACKLIST
from models.user import UserModel
from schemas.user import UserSchema
from models.confirmation import ConfirmationModel

user_schema = UserSchema()


class UserRegister(Resource):

    @classmethod
    def post(cls):
        try:
            user = user_schema.load(request.get_json())
        except ValidationError as e:
            return e.messages, 400

        if UserModel.find_by_username(user.username):
            return {"message": "user with this username already exists"}, 400

        if UserModel.find_by_email(user.email):
            return {"message": "user with this email already exists"}, 400

        try:
            user.save_to_db()
            confirmation = ConfirmationModel(user.id)
            confirmation.save_to_db()
            user.send_confirmation_email()
            return {"message": "Por favor ative no email"}, 201
        except:
            traceback.print_exc()
            return{"message": "erro na criacao"}, 500


class User(Resource):

    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if user:
            return user_schema.dump(user)
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
        try:
            user_json = request.get_json()
            user_data = user_schema.load(user_json, partial=("email",))

        except ValidationError as e:
            return e.messages, 400

        user = UserModel.find_by_username(user_data.username)

        if user and safe_str_cmp(user.password, user_data.password):
            confirmation = user.most_recent_confirmation
            if confirmation and confirmation.confirmed:
                access_token = create_access_token(
                    identity=user.id, fresh=True)
                refresh_token = create_refresh_token(user.id)
                return {"access_token": access_token, "refresh_token": refresh_token}
            return {"message": "Conta não confirmada, por favor, verifique seu email"}, 400
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
