
from flask_restful import Resource
from flask import request
from libs.strings import gettext
from flask_jwt_extended import jwt_required
from models.item import ItemModel
from marshmallow import ValidationError
from schemas.item import ItemSchema

item_schema = ItemSchema()
item_list_schema = ItemSchema(many=True)

class Item(Resource):

    @classmethod
    def get(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            return item_schema.dump(item)
        return {"message":gettext("item_not_found")}, 404

    @classmethod
    @jwt_required
    def post(cls, name: str):
        if ItemModel.find_by_name(name):
            return {"message": gettext("item_already_exist")}, 400
        
        item_json = request.get_json()
        item_json["name"] = name
        try:
            item = item_schema.load(item_json)
        except ValidationError as err:
            return err.messages, 400
        try:
            item.save_to_db()
        except:
            return {"message":gettext("error_500")}, 500
        return item_schema.dump(item), 201

    @classmethod
    @jwt_required
    def delete(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {"message": gettext("item_deleted")}, 201
        return {"message": gettext("item_not_found")}, 404

    @classmethod
    @jwt_required
    def put(cls, name: str):
        item = ItemModel.find_by_name(name)
        item_json = request.get_json()
        if item:
            item.price = item_json["price"]
            item.save_to_db()
            return {"message": gettext("item_updated")}, 200
        item_json["name"] = name
        try:
            item = item_schema.load(item_json)
        except ValidationError as err:
            return err.messages, 400
        item.save_to_db()
        return item_schema.dump(item), 200


class ItemList(Resource):

    @classmethod
    def get(cls):
        return {"items": list(item_list_schema.dump(ItemModel.find_all()))}
