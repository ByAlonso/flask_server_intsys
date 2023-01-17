from flask import Flask, render_template, request, url_for, redirect
from pymongo import MongoClient
from datetime import date, datetime, timedelta
app = Flask(__name__)
client = MongoClient('localhost', 27017)

db = client.fridge
products = db.products
trackedProducts = db.tracked
scannedProducts = db.scanned


@app.route("/api/products", methods=["GET", "POST"])
def getAllProducts():
    if request.method == 'GET':
        return [doc['name'] for doc in products.find({})]
    if request.method == 'POST':
        data = request.get_json()['name'].capitalize()
        print(data)
        products.insert_one({'name': data})
        return "200"


@app.route("/api/scanProducts", methods=["GET", "POST"])
def scanProduct():
    if request.method == 'GET':
        return "TODO"
    if request.method == 'POST':
        data = request.get_json()
        name = data['name']
        tag_id = data['tag_id']

        filter = {'tag_id': tag_id}
        query = {"$set": {'name': name,
            'tag_id': tag_id,
            'registryDate': date.today().strftime("%d/%m/%Y")}}
        if len([x for x in scannedProducts.find(filter)]) > 0:
            scannedProducts.update_one(filter, query)
            if len([x for x in trackedProducts.find(filter)]):
                trackedProducts.update_one(filter,{"$set":{'name':name}})
        else:
            scannedProducts.insert_one(
                {'name': name, 'tag_id': tag_id, 'registryDate': date.today().strftime("%d/%m/%Y")})
        return "200"


@app.route("/api/trackProducts", methods=["GET", "POST"])
def trackProduct():
    if request.method == 'GET':
        return [{'name':doc['name'],'date':doc['registryDate']} for doc in trackedProducts.find({})]
    if request.method == 'POST':
        data = request.get_json()
        tag_id = data['tag_id']
        filter = {'tag_id': tag_id}
        scanned_product = scannedProducts.find(filter)
        tracked_product = trackedProducts.find(filter)
        query = {"$set": {"createdAt": datetime.now()}}
        if len([x for x in tracked_product]) > 0:
            trackedProducts.update_one(filter,query)
        else:
            new_product = [x for x in scanned_product][0]
            trackedProducts.insert_one({'tag_id':new_product['tag_id'],'name':new_product['name'],'registryDate':new_product['registryDate'],"createdAt": datetime.now()})
        return "200"

