from flask_restful import Resource
from models.confirmation import ConfirmationModel
from models.user import UserModel
from schemas.confirmation import ConfirmationSchema
from time import time

confirmation_schema = ConfirmationSchema()

class Confirmation(Resource):
    @classmethod
    def get(cls, confirmation_id: str):
        confirmation = ConfirmationModel.find_by_id(confirmation_id)
        if not confirmation_id or not confirmation:
            return {"message": "não encontrado"}, 404

        if confirmation.expired:
            return {"message": "token expirado"}, 400

        if confirmation.confirmed:
            return {"message": "email ja confirmado"}, 400

        confirmation.confirmed = True
        confirmation.save_to_db()
        return {"message": "email confirmado"}


class ConfirmationByUser(Resource):
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": "nao encontrado"}, 404
        return (
            {
                "current_time": int(time()),
                "confirmation": [
                    confirmation_schema.dump(each) for each in user.confirmation.order_by(ConfirmationModel.expire_at)
                ],
            }, 200
        )

    @classmethod
    def post(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": "nao encontrado"}, 404
        try:
            confirmation = user.most_recent_confirmation
            if confirmation:
                if confirmation.confirmed:
                    return {"message": "ja confirmado"}, 400
                confirmation.force_to_expire()
            new_confirmation = ConfirmationModel(user_id)
            new_confirmation.save_to_db()
            user.send_confirmation_email()
            return {"message": "reenvio realizado"}
        except:
            return{"message" "erro ocorreu"}, 500
