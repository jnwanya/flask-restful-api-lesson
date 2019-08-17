import sqlite3
from flask_restful import Resource, reqparse
from flask_jwt import jwt_required


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price', type=float, required=True, help="This field cannot be left blank")

    @classmethod
    def find_by_name(cls, name):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "SELECT * FROM items where name=?"
        result = cursor.execute(query, (name,))
        row = result.fetchone()
        connection.close()
        if row:
            return {'name': row[1], 'price': row[2]}
        return None

    @classmethod
    def insert_item(cls, item):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "INSERT INTO items VALUES (NULL,?, ?)"
        cursor.execute(query, (item['name'], item['price']))
        connection.commit()
        connection.close()

    @classmethod
    def update_item(cls, item):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = "UPDATE items SET price=? where name=?"
        cursor.execute(query, (item['price'], item['name']))
        connection.commit()
        connection.close()

    @jwt_required()
    def get(self, name):
        item = Item.find_by_name(name)
        if item:
            return {'item': item}, 200
        else:
            return {'message': 'item not found'}, 404

    def post(self, name):
        if Item.find_by_name(name):
            return {'message': 'Item with name: {} already exist'.format(name)}, 400

        # this format the data to json format that in case the content type isn't json. This avoid error.
        # data = request.get_json(force=True)
        data = Item.parser.parse_args()
        item = {'name': name, 'price': data['price']}
        try:
            self.insert_item(item)
        except:
            return {'message', 'An error occurred inserting an item'}, 500
        return item, 201

    def delete(self, name):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "DELETE FROM items WHERE name=?)"
        cursor.execute(query, (name,))
        connection.commit()
        connection.close()

        return {'message': 'item deleted'}, 200

    def put(self, name):
        item = Item.find_by_name(name)
        # data = request.get_json()
        data = Item.parser.parse_args()
        updated_item = {'name': name, 'price': data['price']}
        if item is None:
            self.insert_item(updated_item)
        else:
            self.update_item(updated_item)
        return updated_item


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
