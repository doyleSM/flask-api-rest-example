
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required
from models.item import ItemModel


class Item(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument(
        'price',
        type=float,
        required=True,
        help="esse campo é obrigario"
    )
    parser.add_argument(
        'store_id',
        type=int,
        required=True,
        help="esse campo é obrigario"
    )

    def get(self, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()
        return {"message": "Item not found"}, 404

    @jwt_required
    def post(self, name: str):
        if ItemModel.find_by_name(name):
            return {"message": "Item already exists"}, 400
        data = Item.parser.parse_args()
        item = ItemModel(name, data['price'], data['store_id'])
        try:
            item.save_to_db()
        except:
            return {"message": "ocorreu um erro"}, 500
        return item.json(), 201

    @jwt_required
    def delete(self, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {"message": "item deleted"}, 201
        return {"message": "item not exists"}, 400

    @jwt_required
    def put(self, name: str):
        data = Item.parser.parse_args()
        item = ItemModel.find_by_name(name)
        if item:
            item.price = data['price']
            item.store_id = data['store_id']

            item.save_to_db()
            return {"message": "updated"}, 200

        item = ItemModel(name, **data)
        item.save_to_db()
        return {"message": "created"}, 200


class ItemList(Resource):
    def get(self):
        return {"items": list(item.json() for item in ItemModel.find_all())}
