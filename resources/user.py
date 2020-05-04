import traceback
from flask_restful import Resource, request
from libs.strings import gettext
from werkzeug.security import generate_password_hash, check_password_hash

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
            user.password = generate_password_hash(user.password)
        except ValidationError as e:
            return e.messages, 400

        if UserModel.find_by_username(user.username):
            return {"message": gettext("user_already_exists")}, 400

        if UserModel.find_by_email(user.email):
            return {"message": gettext("email_already_exists")}, 400

        try:
            user.save_to_db()
            confirmation = ConfirmationModel(user.id)
            confirmation.save_to_db()
            user.send_confirmation_email()
            return {"message": gettext("user_created")}, 201
        except:
            traceback.print_exc()
            return{"message": gettext("error_500")}, 500


class User(Resource):

    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if user:
            return user_schema.dump(user)
        return {"message": gettext("user_not_found")}, 404

    @classmethod
    @fresh_jwt_required
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if user:
            user.delete_from_db()
            return {"message": gettext("user_deleted")}
        return {"message": gettext("user_not_found")}, 404


class UserLogin(Resource):

    @classmethod
    def post(cls):
        try:
            user_json = request.get_json()
            user_data = user_schema.load(user_json, partial=("email",))

        except ValidationError as e:
            return e.messages, 400

        user = UserModel.find_by_username(user_data.username)

        if user and check_password_hash(user.password, user_data.password):
            confirmation = user.most_recent_confirmation
            if confirmation and confirmation.confirmed:
                access_token = create_access_token(
                    identity=user.id, fresh=True)
                refresh_token = create_refresh_token(user.id)
                return {"access_token": access_token, "refresh_token": refresh_token}
            return {"message": gettext("user_unconfirmed")}, 400
        return {"message": gettext("wrong_pass_or_user")}, 401


class UserLogout(Resource):

    @classmethod
    @jwt_required
    def post(cls):
        jti = get_raw_jwt()['jti']  # wti = identificador unico do token
        BLACKLIST.add(jti)
        return {"message": gettext("user_logout")}


class TokenRefresh(Resource):

    @classmethod
    @jwt_refresh_token_required
    def post(cls):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}
