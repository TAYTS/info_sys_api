from flask import jsonify
from models import db, Users


def getVendor(vendor_id):
    vendor = db.session.query(
        Users
    ).filter(
        Users,
        Users.id_user_hash == vendor_id,
        Users.is_vendor == 1
    ).scalar()

    if vendor:
        data = {
            'vendor_name': vendor.username,
            'vendor_img': vendor.profile_img_url
        }
    else:
        data = {
            'vendor_name': '',
            'vendor_img': ''
        }

    return jsonify(data)
