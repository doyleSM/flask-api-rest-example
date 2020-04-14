from flask_restful import Resource
from models.store import StoreModel
from schemas.store import StoreSchema


store_schema = StoreSchema()
store_list_schema = StoreSchema(many=True)


class Store(Resource):

    @classmethod
    def get(cls, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            return store_schema.dump(store)
        return {"message": "store nao encontrada"}, 404

    @classmethod
    def post(cls, name: str):
        if StoreModel.find_by_name(name):
            return {"message": "ja existe store"}, 400

        store = StoreModel(name=name)
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
        return {"stores": list(store_list_schema.dump(StoreModel.find_all()))}
