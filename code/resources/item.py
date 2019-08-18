import sqlite3
from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from models.item import ItemModel


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price', type=float, required=True, help="This field cannot be left blank")

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
        item = ItemModel(name, data['price'])
        try:
            item.insert()
        except:
            return {'message', 'An error occurred inserting an item'}, 500
        return item.json(), 201

    def delete(self, name):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "DELETE FROM items WHERE name=?)"
        cursor.execute(query, (name,))
        connection.commit()
        connection.close()

        return {'message': 'item deleted'}, 200

    def put(self, name):
        item = ItemModel.find_by_name(name)
        # data = request.get_json()
        data = Item.parser.parse_args()
        updated_item = ItemModel(name, data['price'])
        if item is None:
            updated_item.insert()
        else:
            updated_item.update()
        return updated_item.json()


class ItemList(Resource):
    def get(self):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "SELECT * FROM items"
        result = cursor.execute(query)
        items = []
        for row in result:
            items.append({'name': row[1], 'price': row[2]})
        connection.close()
        return {"items": items}
