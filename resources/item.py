from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_claims, jwt_optional, get_jwt_identity, fresh_jwt_required
from models.item import ItemModel


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price', type=float, required=True, help="This field cannot be left blank")
    parser.add_argument('storeId', type=int, required=True, help="Store Id field cannot be left blank")

    @jwt_required
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json(), 200
        else:
            return {'message': 'item not found'}, 404

    @fresh_jwt_required
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

    @jwt_required
    def delete(self, name):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {"message": "Admin privilege required."}
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
    @jwt_optional
    def get(self):
        user = get_jwt_identity()
        return {"items": [item.json() for item in ItemModel.find_all()]}
        # return {"items": list(map(lambda item: item.json(), ItemModel.query.all()))}
