from flask_restful import Resource
from libs.strings import gettext
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
        return {"message": gettext("store_not_found")}, 404

    @classmethod
    def post(cls, name: str):
        if StoreModel.find_by_name(name):
            return {"message": gettext("store_already_exists")}, 400

        store = StoreModel(name=name)
        store.save_to_db()

        return {"message": gettext("store_created")}

    @classmethod
    def delete(cls, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()
            return {"message": gettext("store_removed")}
        return {"message": gettext("store_not_found")}, 404


class StoreList(Resource):
    @classmethod
    def get(cls):
        return {"stores": list(store_list_schema.dump(StoreModel.find_all()))}
