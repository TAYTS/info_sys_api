from flask import jsonify, session
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


def listItem(vendor_id=""):
    data = {'data': []}

    # If vendor_id is not present in the GET -> Vendor
    # Get the vendor_id from session
    if not vendor_id:
        # Get the hashed_vendor_id
        vendor_id = str(session.get('id_user'))
        # Verify the vendor_id stored in the session is vendor
        if not session.get('is_vendor', 0):
            return jsonify(data)

    phone_no = db.session.query(
        Users.phone_no
    ).filter(
        Users.id_user_hash == vendor_id
    ).scalar()

    items = db.session.query(
        Items
    ).join(
        Users,
        Items.id_user == Users.id_user
    ).filter(
        Users.id_user_hash == vendor_id,
    ).all()

    if items:
        for item in items:
            temp = {
                'item_name': item.item_name,
                'description': item.description,
                'category': item.category,
                'price': item.price,
                'image_url': item.image_url
            }
            data['data'].append(temp)

    data['phone_no'] = phone_no if phone_no else ""

    return jsonify(data)
