from flask_restful import Resource
from models.store import StoreModel


class Store(Resource):

    @classmethod
    def get(cls, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            return store.json()
        return {"message": "store nao encontrada"}, 404

    @classmethod
    def post(cls, name: str):
        if StoreModel.find_by_name(name):
            return {"message": "ja existe store"}, 400

        store = StoreModel(name)
        store.save_to_db()

        return {"message": "store criada!"}

    @classmethod
    def delete(cls, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()
            return {"message": "removido"}
        return {"message": "store nao encontrada"}, 404


class StoreList(Resource):
    @classmethod
    def get(cls):
        return {"stores": list(store.name for store in StoreModel.find_all())}
