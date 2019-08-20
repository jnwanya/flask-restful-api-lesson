import sqlite3
from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from models.item import ItemModel


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price', type=float, required=True, help="This field cannot be left blank")
    parser.add_argument('storeId', type=int, required=True, help="Store Id field cannot be left blank")

    @jwt_required()
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json(), 200
        else:
            return {'message': 'item not found'}, 404

    def post(self, name):
        if ItemModel.find_by_name(name):
            return {'message': 'Item with name: {} already exist'.format(name)}, 400

        # this format the data to json format that in case the content type isn't json. This avoid error.
        # data = request.get_json(force=True)
        data = Item.parser.parse_args()
        item = ItemModel(name, data['price'], data['storeId'])
        try:
            item.save()
        except:
            return {'message', 'An error occurred inserting an item'}, 500
        return item.json(), 201

    def delete(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete()
        return {'message': 'item deleted'}, 200

    def put(self, name):
        # data = request.get_json()
        data = Item.parser.parse_args()

        item = ItemModel.find_by_name(name)
        if item is None:
            item = ItemModel(name, data['price'], data['storeId'])
        else:
            item.price = data['price']
        item.save()
        return item.json()


class ItemList(Resource):
    def get(self):
        return {"items": [item.json() for item in ItemModel.query.all()]}
        # return {"items": list(map(lambda item: item.json(), ItemModel.query.all()))}
