from flask import jsonify
from models import db, Items, Users


def getItemInfo(vendor_id, item_name):
    item = db.session.query(
        Items
    ).join(
        Users,
        Items.id_user == Users.id_user
    ).filter(
        Users.id_user_hash == vendor_id,
        Items.item_name == item_name
    ).scalar()

    if item:
        description = item.description
        price = item.price
    else:
        description = ''
        price = 0.0

    details = {
        'description': description,
        'price': price
    }

    return jsonify({'details': details})


def listItem(vendor_id):
    items = db.session.query(
        Items
    ).join(
        Users,
        Items.id_user == Users.id_user
    ).filter(
        Users.id_user_hash == vendor_id,
    ).all()

    data = {'data': []}

    if items:
        for item in items:
            temp = {
                'item_name': item.item_name,
                'category': item.category,
                'price': item.price,
                'image_url': item.image_url
            }
            data['data'].append(temp)

    return jsonify(data)
